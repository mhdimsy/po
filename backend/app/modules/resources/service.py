from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

from sqlmodel import Session, select

from app.modules.master_data.models import Machine, MachineProcess, Process, WorkCenter
from app.modules.resources.models import (
    Operator,
    OperatorAvailability,
    OperatorSkill,
    Shift,
    Skill,
    WorkCenterShiftRule,
)
from app.modules.resources.schemas import (
    DistributionItem,
    GenerateOperatorsRequest,
    GenerateOperatorsResponse,
    ShiftRuleInput,
)


DEFAULT_SHIFT_DEFINITIONS = [
    ("SHIFT1", "Shift 1", 6 * 60, 14 * 60),
    ("SHIFT2", "Shift 2", 14 * 60, 22 * 60),
    ("SHIFT3", "Shift 3", 22 * 60, 30 * 60),
]


@dataclass(frozen=True)
class WorkCenterBucket:
    work_center_id: int | None
    title: str
    machine_count: int
    operator_count: int


def generate_operators(session: Session, request: GenerateOperatorsRequest) -> GenerateOperatorsResponse:
    rng = random.Random(request.seed)

    shifts = ensure_default_shifts(session)
    skills = ensure_skills(session)
    shift_rules = ensure_shift_rules(session, shifts, request.shift_rules)
    distribution = propose_distribution(session, request.count)

    process_ids_by_work_center = get_process_ids_by_work_center(session)
    skills_by_process_id = {skill.process_id: skill for skill in skills if skill.process_id is not None}
    fallback_skill = skills[0]

    generated_operators: list[Operator] = []
    generated_operator_skills = 0
    generated_availability_rows = 0
    sequence_start = get_next_operator_sequence(session)

    for bucket in distribution:
        rules_for_work_center = shift_rules.get(bucket.work_center_id) or shift_rules.get(None) or []
        skill_pool = [
            skills_by_process_id[process_id]
            for process_id in process_ids_by_work_center.get(bucket.work_center_id, [])
            if process_id in skills_by_process_id
        ] or skills

        for _ in range(bucket.operator_count):
            sequence = sequence_start + len(generated_operators)
            primary_shift = pick_shift(rng, rules_for_work_center, shifts)
            operator = Operator(
                code=f"OP-SYN-{sequence:05d}",
                full_name=f"Synthetic Operator {sequence:05d}",
                home_work_center_id=bucket.work_center_id,
                primary_shift_id=primary_shift.id,
                status="Available",
                is_synthetic=True,
            )
            session.add(operator)
            session.flush()
            generated_operators.append(operator)

            primary_skill = rng.choice(skill_pool) if skill_pool else fallback_skill
            session.add(
                OperatorSkill(
                    operator_id=operator.id,
                    skill_id=primary_skill.id,
                    level=rng.randint(1, 5),
                    is_primary=True,
                )
            )
            generated_operator_skills += 1

            if rng.random() < request.multi_skill_ratio and len(skills) > 1:
                extra_skill_count = rng.randint(1, min(2, len(skills) - 1))
                extra_skills = [skill for skill in skills if skill.id != primary_skill.id]
                for skill in rng.sample(extra_skills, extra_skill_count):
                    session.add(
                        OperatorSkill(
                            operator_id=operator.id,
                            skill_id=skill.id,
                            level=rng.randint(1, 5),
                            is_primary=False,
                        )
                    )
                    generated_operator_skills += 1

            session.add(
                OperatorAvailability(
                    operator_id=operator.id,
                    work_center_id=bucket.work_center_id,
                    shift_id=primary_shift.id,
                    status="Available",
                )
            )
            generated_availability_rows += 1

    session.commit()

    return GenerateOperatorsResponse(
        requested_count=request.count,
        generated_operators=len(generated_operators),
        generated_operator_skills=generated_operator_skills,
        generated_availability_rows=generated_availability_rows,
        skills_count=len(skills),
        shifts_count=len(shifts),
        work_center_shift_rules_count=sum(len(items) for items in shift_rules.values()),
        multi_skill_ratio=request.multi_skill_ratio,
        distribution=[
            DistributionItem(
                work_center_id=item.work_center_id,
                work_center_title=item.title,
                machine_count=item.machine_count,
                operator_count=item.operator_count,
            )
            for item in distribution
        ],
    )


def ensure_default_shifts(session: Session) -> list[Shift]:
    shifts: list[Shift] = []
    for code, title, start, end in DEFAULT_SHIFT_DEFINITIONS:
        shift = session.exec(select(Shift).where(Shift.code == code)).first()
        if shift is None:
            shift = Shift(code=code, title=title, start_minute_of_day=start, end_minute_of_day=end)
            session.add(shift)
            session.flush()
        shifts.append(shift)
    return shifts


def ensure_skills(session: Session) -> list[Skill]:
    processes = session.exec(select(Process)).all()
    skills: list[Skill] = []
    if not processes:
        default_skill = session.exec(select(Skill).where(Skill.code == "GENERAL")).first()
        if default_skill is None:
            default_skill = Skill(code="GENERAL", title="General Production Skill", process_id=None)
            session.add(default_skill)
            session.flush()
        return [default_skill]

    for process in processes:
        code = f"PROCESS-{process.source_process_id}"
        skill = session.exec(select(Skill).where(Skill.code == code)).first()
        if skill is None:
            skill = Skill(
                code=code,
                title=process.title or f"Process {process.source_process_id}",
                process_id=process.source_process_id,
            )
            session.add(skill)
            session.flush()
        skills.append(skill)
    return skills


def ensure_shift_rules(
    session: Session,
    shifts: list[Shift],
    requested_rules: list[ShiftRuleInput],
) -> dict[int | None, list[WorkCenterShiftRule]]:
    shift_by_code = {shift.code: shift for shift in shifts}
    rules_by_work_center: dict[int | None, list[WorkCenterShiftRule]] = defaultdict(list)
    rules_to_apply = requested_rules or [
        ShiftRuleInput(work_center_id=None, shift_code="SHIFT1", ratio=0.4),
        ShiftRuleInput(work_center_id=None, shift_code="SHIFT2", ratio=0.4),
        ShiftRuleInput(work_center_id=None, shift_code="SHIFT3", ratio=0.2),
    ]

    for rule_input in rules_to_apply:
        shift = shift_by_code.get(rule_input.shift_code)
        if shift is None:
            continue
        rule = session.exec(
            select(WorkCenterShiftRule).where(
                WorkCenterShiftRule.work_center_id == rule_input.work_center_id,
                WorkCenterShiftRule.shift_id == shift.id,
            )
        ).first()
        if rule is None:
            rule = WorkCenterShiftRule(
                work_center_id=rule_input.work_center_id,
                shift_id=shift.id,
                ratio=rule_input.ratio,
            )
            session.add(rule)
            session.flush()
        else:
            rule.ratio = rule_input.ratio
            session.add(rule)
        rules_by_work_center[rule.work_center_id].append(rule)
    return rules_by_work_center


def propose_distribution(session: Session, operator_count: int) -> list[WorkCenterBucket]:
    work_centers = session.exec(select(WorkCenter)).all()
    machines = session.exec(select(Machine)).all()

    if not work_centers:
        return [WorkCenterBucket(None, "General", len(machines), operator_count)]

    machine_count_by_work_center: dict[int, int] = defaultdict(int)
    for machine in machines:
        machine_count_by_work_center[machine.work_center_id] += 1

    weighted_work_centers = [
        (work_center, max(1, machine_count_by_work_center.get(work_center.source_work_center_id, 0)))
        for work_center in work_centers
    ]
    total_weight = sum(weight for _, weight in weighted_work_centers)

    buckets: list[WorkCenterBucket] = []
    assigned = 0
    remainders: list[tuple[float, int]] = []
    for index, (work_center, weight) in enumerate(weighted_work_centers):
        exact_count = operator_count * weight / total_weight
        count = int(exact_count)
        assigned += count
        remainders.append((exact_count - count, index))
        buckets.append(
            WorkCenterBucket(
                work_center.source_work_center_id,
                work_center.title or work_center.code or f"WorkCenter {work_center.source_work_center_id}",
                machine_count_by_work_center.get(work_center.source_work_center_id, 0),
                count,
            )
        )

    remaining = operator_count - assigned
    for _, index in sorted(remainders, reverse=True)[:remaining]:
        bucket = buckets[index]
        buckets[index] = WorkCenterBucket(
            bucket.work_center_id,
            bucket.title,
            bucket.machine_count,
            bucket.operator_count + 1,
        )
    return buckets


def get_process_ids_by_work_center(session: Session) -> dict[int | None, list[int]]:
    machines = session.exec(select(Machine)).all()
    machine_processes = session.exec(select(MachineProcess)).all()
    machine_to_work_center = {machine.source_machine_id: machine.work_center_id for machine in machines}
    process_ids_by_work_center: dict[int | None, set[int]] = defaultdict(set)

    for capability in machine_processes:
        work_center_id = machine_to_work_center.get(capability.machine_id)
        process_ids_by_work_center[work_center_id].add(capability.process_id)

    return {
        work_center_id: sorted(process_ids)
        for work_center_id, process_ids in process_ids_by_work_center.items()
    }


def pick_shift(
    rng: random.Random,
    rules: list[WorkCenterShiftRule],
    shifts: list[Shift],
) -> Shift:
    if not rules:
        return shifts[0]
    total_ratio = sum(max(0, rule.ratio) for rule in rules)
    if total_ratio <= 0:
        return shifts[0]

    target = rng.random() * total_ratio
    cumulative = 0.0
    shift_by_id = {shift.id: shift for shift in shifts}
    for rule in rules:
        cumulative += max(0, rule.ratio)
        if target <= cumulative and rule.shift_id in shift_by_id:
            return shift_by_id[rule.shift_id]
    return shifts[0]


def get_next_operator_sequence(session: Session) -> int:
    current_count = len(session.exec(select(Operator)).all())
    return current_count + 1
