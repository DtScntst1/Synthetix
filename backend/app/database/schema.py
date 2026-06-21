from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

# -------------------------------------------------------------------
# Core Graph Schema (Entity and Relationships)
# -------------------------------------------------------------------

class GraphNode(BaseModel):
    """
    Represents an Entity (Node) in the Neo4j Knowledge Graph.
    Includes temporal tracking and Role-Based Access Control (RBAC).
    """
    id: str = Field(..., description="Unique identifier for the node (e.g., 'COMPANY_APPLE')")
    label: str = Field(..., description="The type/label of the entity (e.g., 'Organization', 'Person', 'Statistic')")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs containing entity attributes")
    
    # Temporal (Time-based) tracking
    valid_from: Optional[datetime] = Field(default=None, description="When this node became valid/active")
    valid_to: Optional[datetime] = Field(default=None, description="When this node ceased to be valid")
    
    # Security / RBAC
    clearance_level: int = Field(default=0, description="Minimum clearance level required to access this node. 0=Public, 1=Internal, 2=Confidential, 3=Secret")
    
    # Traceability
    source_document_id: Optional[str] = Field(default=None, description="ID of the document from which this entity was extracted")
    source_page_number: Optional[int] = Field(default=None, description="Page number for UI highlighting")

class GraphEdge(BaseModel):
    """
    Represents a Relationship (Edge) between two nodes in Neo4j.
    """
    source_id: str = Field(..., description="ID of the source node")
    target_id: str = Field(..., description="ID of the target node")
    type: str = Field(..., description="Relationship type (e.g., 'ACQUIRED', 'REPORTED_REVENUE', 'CORRELATED_WITH')")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Attributes of the relationship (e.g., weight, confidence, p-value)")
    
    # Temporal tracking for the relationship itself
    valid_from: Optional[datetime] = Field(default=None)
    valid_to: Optional[datetime] = Field(default=None)

# -------------------------------------------------------------------
# Quantitative & Visual Data Schemas (For Specialized Agents)
# -------------------------------------------------------------------

class QuantitativeData(BaseModel):
    """
    Structured format for tables extracted by the Quantitative Agent.
    """
    metric_name: str
    value: float
    unit: str
    p_value: Optional[float] = None
    confidence_interval: Optional[str] = None
    year: Optional[int] = None

class VisualInsight(BaseModel):
    """
    Insight extracted from charts/graphs by the Vision Agent.
    """
    chart_type: str = Field(..., description="e.g., 'Pie Chart', 'Trend Line'")
    key_takeaway: str = Field(..., description="The main insight from the chart")
    trend_direction: Optional[str] = Field(default=None, description="e.g., 'Upward', 'Downward', 'Stable'")
    source_image_path: str
