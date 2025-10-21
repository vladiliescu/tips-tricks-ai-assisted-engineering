from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.team import (
    Team,
    TeamMember,
    TechnologyExperience,
    Sprint,
    SeniorityLevel,
    ExperienceLevel,
)

router = APIRouter()


# Pydantic models for API requests and responses
class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    current_size: int
    average_velocity: Optional[float]
    average_cycle_time_hours: Optional[float]
    estimation_accuracy_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberCreate(BaseModel):
    name: str
    email: Optional[str] = None
    github_username: Optional[str] = None
    seniority_level: SeniorityLevel = SeniorityLevel.MID
    years_of_experience: Optional[float] = None
    hourly_rate: Optional[float] = None


class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    github_username: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = None
    years_of_experience: Optional[float] = None
    hourly_rate: Optional[float] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    github_username: Optional[str]
    seniority_level: SeniorityLevel
    years_of_experience: Optional[float]
    is_active: bool
    tenure_months: Optional[float]
    joined_team_at: datetime

    class Config:
        from_attributes = True


class TechnologyExperienceCreate(BaseModel):
    technology_name: str
    category: Optional[str] = None
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    years_of_experience: Optional[float] = None
    proficiency_score: Optional[float] = None
    is_primary_skill: bool = False
    notes: Optional[str] = None


class TechnologyExperienceResponse(BaseModel):
    id: int
    technology_name: str
    category: Optional[str]
    experience_level: ExperienceLevel
    years_of_experience: Optional[float]
    proficiency_score: Optional[float]
    is_primary_skill: bool
    is_current_skill: bool
    notes: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """
    List all teams.
    """
    query = db.query(Team)

    if active_only:
        query = query.filter(Team.is_active == True)

    teams = query.offset(skip).limit(limit).all()
    return teams


@router.post("/", response_model=TeamResponse)
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """
    Create a new team.
    """
    # Check if team name already exists
    existing_team = db.query(Team).filter(Team.name == team_data.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists")

    team = Team(
        name=team_data.name,
        description=team_data.description,
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return team


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    Get a specific team by ID.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int, team_update: TeamUpdate, db: Session = Depends(get_db)
):
    """
    Update a team.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Update fields if provided
    if team_update.name is not None:
        # Check if new name already exists (excluding current team)
        existing_team = (
            db.query(Team)
            .filter(Team.name == team_update.name, Team.id != team_id)
            .first()
        )
        if existing_team:
            raise HTTPException(status_code=400, detail="Team name already exists")
        team.name = team_update.name

    if team_update.description is not None:
        team.description = team_update.description

    if team_update.is_active is not None:
        team.is_active = team_update.is_active

    db.commit()
    db.refresh(team)

    return team


@router.delete("/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    """
    Delete a team (soft delete by setting is_active to False).
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.is_active = False
    db.commit()

    return {"message": f"Team {team.name} has been deactivated"}


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """
    List all members of a specific team.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    query = db.query(TeamMember).filter(TeamMember.team_id == team_id)

    if active_only:
        query = query.filter(TeamMember.is_active == True)

    members = query.all()
    return members


@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: int, member_data: TeamMemberCreate, db: Session = Depends(get_db)
):
    """
    Add a new member to a team.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if email already exists in the team
    if member_data.email:
        existing_member = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.email == member_data.email,
                TeamMember.is_active == True,
            )
            .first()
        )
        if existing_member:
            raise HTTPException(
                status_code=400,
                detail="Member with this email already exists in the team",
            )

    member = TeamMember(
        team_id=team_id,
        name=member_data.name,
        email=member_data.email,
        github_username=member_data.github_username,
        seniority_level=member_data.seniority_level,
        years_of_experience=member_data.years_of_experience,
        hourly_rate=member_data.hourly_rate,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


@router.get("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(team_id: int, member_id: int, db: Session = Depends(get_db)):
    """
    Get a specific team member.
    """
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return member


@router.put("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: int,
    member_id: int,
    member_update: TeamMemberUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a team member.
    """
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    # Update fields if provided
    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    db.commit()
    db.refresh(member)

    return member


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: int, member_id: int, db: Session = Depends(get_db)
):
    """
    Remove a member from a team (soft delete).
    """
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    member.is_active = False
    member.left_team_at = datetime.utcnow()
    db.commit()

    return {"message": f"Member {member.name} has been removed from the team"}


@router.get(
    "/{team_id}/members/{member_id}/technologies",
    response_model=List[TechnologyExperienceResponse],
)
async def list_member_technologies(
    team_id: int, member_id: int, db: Session = Depends(get_db)
):
    """
    List technology experiences for a team member.
    """
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    technologies = (
        db.query(TechnologyExperience)
        .filter(TechnologyExperience.team_member_id == member_id)
        .all()
    )

    return technologies


@router.post(
    "/{team_id}/members/{member_id}/technologies",
    response_model=TechnologyExperienceResponse,
)
async def add_member_technology(
    team_id: int,
    member_id: int,
    tech_data: TechnologyExperienceCreate,
    db: Session = Depends(get_db),
):
    """
    Add technology experience for a team member.
    """
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")

    # Check if technology already exists for this member
    existing_tech = (
        db.query(TechnologyExperience)
        .filter(
            TechnologyExperience.team_member_id == member_id,
            TechnologyExperience.technology_name == tech_data.technology_name,
        )
        .first()
    )
    if existing_tech:
        raise HTTPException(
            status_code=400,
            detail="Technology experience already exists for this member",
        )

    technology = TechnologyExperience(
        team_member_id=member_id,
        technology_name=tech_data.technology_name,
        category=tech_data.category,
        experience_level=tech_data.experience_level,
        years_of_experience=tech_data.years_of_experience,
        proficiency_score=tech_data.proficiency_score,
        is_primary_skill=tech_data.is_primary_skill,
        notes=tech_data.notes,
    )

    db.add(technology)
    db.commit()
    db.refresh(technology)

    return technology


@router.get("/{team_id}/analytics")
async def get_team_analytics(team_id: int, db: Session = Depends(get_db)):
    """
    Get analytics for a specific team.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Get active members
    active_members = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.is_active == True)
        .all()
    )

    # Calculate seniority distribution
    seniority_dist = team.seniority_distribution

    # Calculate average experience
    avg_experience = None
    if active_members:
        experiences = [
            m.years_of_experience for m in active_members if m.years_of_experience
        ]
        if experiences:
            avg_experience = sum(experiences) / len(experiences)

    # Get technology overview
    all_techs = (
        db.query(TechnologyExperience)
        .join(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.is_active == True)
        .all()
    )

    tech_summary = {}
    for tech in all_techs:
        if tech.technology_name not in tech_summary:
            tech_summary[tech.technology_name] = {
                "count": 0,
                "avg_proficiency": 0,
                "experience_levels": [],
            }
        tech_summary[tech.technology_name]["count"] += 1
        tech_summary[tech.technology_name]["experience_levels"].append(
            tech.experience_level.value
        )
        if tech.proficiency_score:
            current_avg = tech_summary[tech.technology_name]["avg_proficiency"]
            count = tech_summary[tech.technology_name]["count"]
            tech_summary[tech.technology_name]["avg_proficiency"] = (
                current_avg * (count - 1) + tech.proficiency_score
            ) / count

    return {
        "team_name": team.name,
        "team_size": team.current_size,
        "seniority_distribution": seniority_dist,
        "average_years_experience": avg_experience,
        "average_velocity": team.average_velocity,
        "average_cycle_time_hours": team.average_cycle_time_hours,
        "estimation_accuracy_score": team.estimation_accuracy_score,
        "technology_summary": tech_summary,
        "is_active": team.is_active,
    }


@router.get("/health")
async def teams_health_check():
    """
    Health check for teams API.
    """
    return {"status": "healthy", "service": "teams"}
