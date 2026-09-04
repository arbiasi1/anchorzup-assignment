from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Rule
from .processor import process_text
from .schemas import ProcessRequest, ProcessResponse, RuleCreate, RuleOut, RuleUpdate

router = APIRouter(prefix="/api")


def find_rule(rule_id: int, db: Session) -> Rule:
    rule = db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/rules", response_model=list[RuleOut])
def list_rules(db: Session = Depends(get_db)):
    return db.scalars(select(Rule).order_by(Rule.priority.desc(), Rule.created_at.desc())).all()


@router.post("/rules", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    rule = Rule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}", response_model=RuleOut)
def update_rule(rule_id: int, payload: RuleUpdate, db: Session = Depends(get_db)):
    rule = find_rule(rule_id, db)
    values = payload.model_dump(exclude_unset=True)
    combined = RuleCreate.model_validate({
        "keyword": values.get("keyword", rule.keyword),
        "match_type": values.get("match_type", rule.match_type),
        "action_type": values.get("action_type", rule.action_type),
        "color": values.get("color", rule.color),
        "label": values.get("label", rule.label),
        "priority": values.get("priority", rule.priority),
        "enabled": values.get("enabled", rule.enabled),
        "case_sensitive": values.get("case_sensitive", rule.case_sensitive),
    })
    for key, value in combined.model_dump().items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    db.delete(find_rule(rule_id, db))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/process", response_model=ProcessResponse)
def process(payload: ProcessRequest, db: Session = Depends(get_db)):
    rules = db.scalars(select(Rule).where(Rule.enabled.is_(True))).all()
    return process_text(payload.text, rules)

