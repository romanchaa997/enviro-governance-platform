"""SQLAlchemy models for enviro-governance-platform database."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    role = Column(String(50), default="user")  # user, admin, analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    remediation_plans = relationship("RemediationPlan", back_populates="creator")
    decisions = relationship("Decision", back_populates="creator")


class Organization(Base):
    """Organization/customer model for B2B SaaS."""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    website = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default="free")  # free, basic, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    remediation_plans = relationship("RemediationPlan", back_populates="organization")
    decisions = relationship("Decision", back_populates="organization")


class RemediationPlan(Base):
    """Generated remediation strategies."""
    __tablename__ = "remediation_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    pollution_description = Column(String(2000), nullable=False)
    site_type = Column(String(100), nullable=False)  # wastewater_treatment_plant, contaminated_land, etc
    location = Column(String(255), nullable=False)
    budget_tier = Column(String(50), nullable=False)  # low, medium, high
    strategies = Column(JSON, nullable=False)  # Array of strategy objects
    selected_strategy_index = Column(Integer, nullable=True)
    status = Column(String(50), default="draft")  # draft, active, completed, archived
    notes = Column(String(2000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="remediation_plans")
    organization = relationship("Organization", back_populates="remediation_plans")


class Agent(Base):
    """Remediation agent configuration."""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String(100), nullable=False, index=True)  # fungal, bacterial, crispr, llm_explainer
    name = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    effectiveness_range = Column(JSON, nullable=True)  # {"min": 0.7, "max": 0.95}
    cost_estimate_range = Column(JSON, nullable=True)  # {"min": 10000, "max": 50000}
    timeline_days_range = Column(JSON, nullable=True)  # {"min": 30, "max": 180}
    parameters = Column(JSON, nullable=True)  # Agent-specific configuration
    is_active = Column(Boolean, default=True)
    version = Column(String(50), default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Decision(Base):
    """Policy decisions with voting data."""
    __tablename__ = "decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    policy_description = Column(String(2000), nullable=False)
    voting_data = Column(JSON, nullable=False)  # {voters: [...], vectors: [...]}
    aggregate_score = Column(Float, nullable=False)  # -1.0 to 1.0
    vector_breakdown = Column(JSON, nullable=False)  # {vector_name: score, ...}
    voter_consensus = Column(Float, nullable=False)  # 0.0 to 1.0
    recommendation = Column(String(50), nullable=False)  # APPROVE, REJECT, NEEDS_REVIEW
    status = Column(String(50), default="pending")  # pending, approved, rejected, implemented
    audit_log_id = Column(UUID(as_uuid=True), ForeignKey("audit_logs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="decisions")
    organization = relationship("Organization", back_populates="decisions")


class AuditLog(Base):
    """Audit trail for governance transparency."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)  # create, update, delete, vote, etc
    resource_type = Column(String(100), nullable=False)  # user, decision, remediation_plan, etc
    resource_id = Column(String(255), nullable=False)
    changes = Column(JSON, nullable=True)  # {old: {...}, new: {...}}
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)
    status = Column(String(50), default="success")  # success, failure
    error_message = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class VotingVector(Base):
    """Voting vector configuration for governance engine."""
    __tablename__ = "voting_vectors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    range_min = Column(Float, default=-1.0)
    range_max = Column(Float, default=1.0)
    default_weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
