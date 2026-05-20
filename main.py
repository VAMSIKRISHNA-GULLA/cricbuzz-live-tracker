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
    deliveries_in_over = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == delivery.match_id,
        DeliveryModel.over == delivery.over
    ).all()

    legal_balls = sum(
        1 for d in deliveries_in_over
        if d.extra_type not in ["wide", "no-ball"]
    )

    current_delivery_is_legal = delivery.extra_type not in ["wide", "no-ball"]

    if legal_balls >= 6 and current_delivery_is_legal:
        return {
            "error": "Over already completed with 6 legal deliveries"
        }

    match = db.query(MatchModel).filter(
        MatchModel.id == delivery.match_id
    ).first()

    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == delivery.match_id
    ).all()

    wickets = sum(
        1 for d in deliveries
        if d.wicket
    )

    legal_balls = sum(
        1 for d in deliveries
        if d.extra_type not in ["wide", "no-ball"]
    )

    if match.format == "T20" and legal_balls >= 120:
        return {
            "error": "Innings completed for T20"
        }

    if match.format == "ODI" and legal_balls >= 300:
        return {
            "error": "Innings completed for ODI"
        }

    if wickets >= 10:
        return {
            "error": "All wickets are down"
        }

    bowler_deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == delivery.match_id,
        DeliveryModel.bowler == delivery.bowler
    ).all()

    bowler_legal_balls = sum(
        1 for d in bowler_deliveries
        if d.extra_type not in ["wide", "no-ball"]
    )

    bowler_overs = bowler_legal_balls / 6

    if match.format == "T20" and bowler_overs >= 4:
        return {
            "error": "Bowler exceeded maximum overs limit"
        }

    if match.format == "ODI" and bowler_overs >= 10:
        return {
            "error": "Bowler exceeded maximum overs limit"
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

@app.get("/batsman/{name}")
def batsman_scorecard(name: str):

    db: Session = SessionLocal()

    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.batsman == name
    ).all()

    runs = sum(delivery.runs for delivery in deliveries)

    balls = len(deliveries)

    return {
        "batsman": name,
        "runs": runs,
        "balls": balls
    }

@app.get("/bowler/{name}")
def bowler_figures(name: str):

    db: Session = SessionLocal()

    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.bowler == name
    ).all()

    runs_conceded = sum(delivery.runs for delivery in deliveries)

    wickets = sum(
        1 for delivery in deliveries
        if delivery.wicket
    )

    legal_balls = sum(
        1 for delivery in deliveries
        if delivery.extra_type not in ["wide", "no-ball"]
    )

    overs = f"{legal_balls // 6}.{legal_balls % 6}"

    overs_float = legal_balls / 6

    if overs_float > 0:
        economy = round(runs_conceded / overs_float, 2)
    else:
        economy = 0

    return {
        "bowler": name,
        "overs": overs,
        "runs_conceded": runs_conceded,
        "wickets": wickets,
        "economy": economy
    }

@app.get("/partnership/{match_id}")
def partnership_tracker(match_id: int):

    db: Session = SessionLocal()

    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == match_id
    ).all()

    total_runs = sum(d.runs for d in deliveries)

    total_balls = len([
        d for d in deliveries
        if d.extra_type not in ["wide", "no-ball"]
    ])

    return {
        "match_id": match_id,
        "partnership_runs": total_runs,
        "balls_faced": total_balls
    }

@app.get("/match-summary/{match_id}")
def match_summary(match_id: int):

    db: Session = SessionLocal()

    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.match_id == match_id
    ).all()

    total_runs = sum(d.runs for d in deliveries)

    wickets = len([
        d for d in deliveries
        if d.wicket
    ])

    fall_of_wickets = []

    current_score = 0

    for d in deliveries:

        current_score += d.runs

        if d.wicket:

            fall_of_wickets.append({
                "player": d.wicket,
                "score": current_score
            })

    return {
        "final_score": f"{total_runs}/{wickets}",
        "fall_of_wickets": fall_of_wickets,
        "player_of_match": "To be decided"
    }

@app.get("/head-to-head")
def head_to_head(teamA: str, teamB: str):

    db: Session = SessionLocal()

    matches = db.query(MatchModel).filter(
        (
            (MatchModel.teamA == teamA) &
            (MatchModel.teamB == teamB)
        ) |
        (
            (MatchModel.teamA == teamB) &
            (MatchModel.teamB == teamA)
        )
    ).all()

    total_matches = len(matches)

    return {
        "teamA": teamA,
        "teamB": teamB,
        "matches_played": total_matches
    }

