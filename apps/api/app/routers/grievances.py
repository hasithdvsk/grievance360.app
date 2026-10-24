from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()


class GrievanceCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200, example="Potable water contamination in Ward 7")
    description: str = Field(..., min_length=20, example="For the past 4 days, tap water supplied to block B has high turbidity and foul odor.")
    category: str = Field(..., example="Water Supply & Sanitation")
    citizen_name: str = Field(..., example="Aarav Sharma")
    citizen_email: str = Field(..., example="aarav@example.com")
    location: str = Field(..., example="Ward 7, Sector 12")


class GrievanceResponse(BaseModel):
    id: str
    ticket_id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    department: str
    citizen_name: str
    created_at: str
    updated_at: str


# In-memory mock storage for initial scaffold
MOCK_GRIEVANCES: List[dict] = [
    {
        "id": "1",
        "ticket_id": "GRV-2026-00101",
        "title": "High voltage fluctuation damaging electronic meters",
        "description": "Repeated voltage spikes observed between 6 PM to 9 PM, caused transformer trip.",
        "category": "Electricity & Power",
        "priority": "HIGH",
        "status": "IN_PROGRESS",
        "department": "Public Works & Energy",
        "citizen_name": "Priya Nair",
        "created_at": "2026-10-22T09:30:00Z",
        "updated_at": "2026-10-23T04:15:00Z",
    },
    {
        "id": "2",
        "ticket_id": "GRV-2026-00102",
        "title": "Uncollected commercial waste near Central Market road",
        "description": "Garbage bins overflowing since last Monday causing severe pedestrian blockage.",
        "category": "Sanitation & Waste Management",
        "priority": "MEDIUM",
        "status": "OPEN",
        "department": "Municipal Solid Waste",
        "citizen_name": "Rajesh Gupta",
        "created_at": "2026-10-23T06:45:00Z",
        "updated_at": "2026-10-23T06:45:00Z",
    },
]


@router.get("/", response_model=List[GrievanceResponse])
async def list_grievances(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, IN_PROGRESS, RESOLVED)"),
    category: Optional[str] = Query(None, description="Filter by grievance category"),
):
    """
    Retrieve paginated grievance tickets with optional filter by status and category.
    """
    results = MOCK_GRIEVANCES
    if status:
        results = [g for g in results if g["status"].upper() == status.upper()]
    if category:
        results = [g for g in results if g["category"].lower() == category.lower()]
    return results


@router.post("/", response_model=GrievanceResponse, status_code=201)
async def create_grievance(payload: GrievanceCreate):
    """
    File a new citizen grievance. Triggers AI semantic categorization and SLA tagging.
    """
    new_id = str(uuid.uuid4())
    ticket_num = f"GRV-2026-{len(MOCK_GRIEVANCES) + 101:05d}"
    now = datetime.utcnow().isoformat() + "Z"

    record = {
        "id": new_id,
        "ticket_id": ticket_num,
        "title": payload.title,
        "description": payload.description,
        "category": payload.category,
        "priority": "MEDIUM",  # Computed by sentence-transformer in full pipeline
        "status": "OPEN",
        "department": "Municipal Grievance Cell",
        "citizen_name": payload.citizen_name,
        "created_at": now,
        "updated_at": now,
    }
    MOCK_GRIEVANCES.append(record)
    return record


@router.get("/{ticket_id}", response_model=GrievanceResponse)
async def get_grievance(ticket_id: str):
    """
    Fetch a single grievance ticket by ticket ID.
    """
    for g in MOCK_GRIEVANCES:
        if g["ticket_id"] == ticket_id or g["id"] == ticket_id:
            return g
    raise HTTPException(status_code=404, detail="Grievance ticket not found")
