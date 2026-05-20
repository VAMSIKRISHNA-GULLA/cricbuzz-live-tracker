from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models.match import Match as MatchModel
from models.player import Player as PlayerModel
from models.delivery import Delivery as DeliveryModel

# =========================
# CREATE TABLES
# =========================

Base.metadata.create_all(bind=engine)

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# REQUEST MODELS
# =========================

class Match(BaseModel):
    teamA: str
    teamB: str
    venue: str
    format: str


class Player(BaseModel):
    name: str
    role: str
    batting_style: str
    bowling_style: str
    team: str
    match_id: int


class Delivery(BaseModel):
    match_id: int
    over: int
    ball: int
    batsman: str
    bowler: str
    runs: int
    extra_type: str | None = None
    wicket: str | None = None


# =========================
# HOME API
# =========================

@app.get("/")
def home():
    return {"message": "Cricbuzz API Running"}


# =========================
# CREATE MATCH
# =========================

@app.post("/match")
def create_match(match: Match):

    db: Session = SessionLocal()

    new_match = MatchModel(
        teamA=match.teamA,
        teamB=match.teamB,
        venue=match.venue,
        format=match.format
    )

    db.add(new_match)

    db.commit()

    db.refresh(new_match)

    return {
        "message": "Match saved successfully",
        "match_id": new_match.id
    }


# =========================
# GET ALL MATCHES
# =========================

@app.get("/matches")
def get_matches():

    db: Session = SessionLocal()

    matches = db.query(MatchModel).all()

    return matches


# =========================
# CREATE PLAYER
# =========================

@app.post("/player")
def create_player(player: Player):

    db: Session = SessionLocal()

    new_player = PlayerModel(
        name=player.name,
        role=player.role,
        batting_style=player.batting_style,
        bowling_style=player.bowling_style,
        team=player.team,
        match_id=player.match_id
    )

    db.add(new_player)

    db.commit()

    db.refresh(new_player)

    return {
        "message": "Player added successfully",
        "player_id": new_player.id
    }


# =========================
# RECORD DELIVERY
# =========================

@app.post("/delivery")
def record_delivery(delivery: Delivery):

    db: Session = SessionLocal()

    # CHECK DUPLICATE BALL
    existing_delivery = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == delivery.match_id,
        DeliveryModel.over == delivery.over,
        DeliveryModel.ball == delivery.ball
    ).first()

    if existing_delivery:
        return {
            "error": "This ball already exists"
        }

    new_delivery = DeliveryModel(
        match_id=delivery.match_id,
        over=delivery.over,
        ball=delivery.ball,
        batsman=delivery.batsman,
        bowler=delivery.bowler,
        runs=delivery.runs,
        extra_type=delivery.extra_type,
        wicket=delivery.wicket
    )

    db.add(new_delivery)

    db.commit()

    db.refresh(new_delivery)

    return {
        "message": "Delivery recorded successfully",
        "delivery_id": new_delivery.id
    }


# =========================
# LIVE SCORECARD
# =========================

@app.get("/scorecard/{match_id}")
def get_scorecard(match_id: int):

    db: Session = SessionLocal()

    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == match_id
    ).all()

    total_runs = sum(delivery.runs for delivery in deliveries)

    wickets = sum(1 for delivery in deliveries if delivery.wicket)

    legal_balls = 0

    for delivery in deliveries:
        if delivery.extra_type not in ["wide", "no-ball"]:
            legal_balls += 1

    overs = f"{legal_balls // 6}.{legal_balls % 6}"

    overs_float = legal_balls / 6

    if overs_float > 0:
        run_rate = round(total_runs / overs_float, 2)
    else:
        run_rate = 0

    return {
        "score": f"{total_runs}/{wickets}",
        "overs": overs,
        "run_rate": run_rate
    }