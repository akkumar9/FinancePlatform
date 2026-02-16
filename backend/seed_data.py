"""
Seed realistic data for demo
"""

from datetime import datetime, timedelta
from database import (
    CASES_DB, MESSAGES_DB, RESOURCES_DB,
    Case, Message, Resource,
    UrgencyLevel, Category, Sentiment
)

def seed_resources():
    """Add realistic financial resources"""
    resources = [
        Resource(
            id="res_1",
            name="Amazon Employee Hardship Fund",
            description="Emergency financial assistance for Amazon employees facing unexpected crises",
            category=Category.OTHER,
            eligibility_criteria="Amazon employees with 6+ months tenure, documented emergency",
            max_amount=2000,
            typical_approval_time="2-3 business days",
            application_difficulty="easy",
            success_rate=0.85,
            contact_info="Apply through AtoZ app or HR portal",
            location="National"
        ),
        Resource(
            id="res_2",
            name="Oakland Emergency Rental Assistance",
            description="City of Oakland program providing up to 3 months rent",
            category=Category.RENT,
            eligibility_criteria="Oakland residents, income <80% AMI, documented hardship",
            max_amount=6000,
            typical_approval_time="2-3 weeks",
            application_difficulty="moderate",
            success_rate=0.65,
            contact_info="oaklandca.gov/rental-assistance",
            location="Oakland, CA"
        ),
        Resource(
            id="res_3",
            name="Bay Area Credit Union Emergency Loan",
            description="Small dollar loans for emergencies, low credit scores accepted",
            category=Category.DEBT,
            eligibility_criteria="Credit score >500, verifiable income",
            max_amount=1500,
            typical_approval_time="1-2 business days",
            application_difficulty="easy",
            success_rate=0.75,
            contact_info="www.bacreditunion.org",
            location="Bay Area, CA"
        ),
        Resource(
            id="res_4",
            name="PG&E CARE Program",
            description="20-35% discount on electricity and gas bills",
            category=Category.UTILITIES,
            eligibility_criteria="Income <200% federal poverty level",
            max_amount=None,
            typical_approval_time="2-4 weeks",
            application_difficulty="easy",
            success_rate=0.90,
            contact_info="1-800-743-5000",
            location="Northern California"
        ),
        Resource(
            id="res_5",
            name="CalFresh (Food Stamps)",
            description="Monthly food assistance for low-income California residents",
            category=Category.FOOD,
            eligibility_criteria="Income <200% federal poverty level",
            max_amount=None,
            typical_approval_time="30 days",
            application_difficulty="moderate",
            success_rate=0.80,
            contact_info="www.getcalfresh.org",
            location="California"
        ),
        Resource(
            id="res_6",
            name="Kaiser Permanente Employee Assistance",
            description="Financial counseling and emergency grants for Kaiser employees",
            category=Category.MEDICAL,
            eligibility_criteria="Kaiser employees",
            max_amount=1000,
            typical_approval_time="1 week",
            application_difficulty="easy",
            success_rate=0.78,
            contact_info="HR portal or 1-800-555-HELP",
            location="National"
        ),
        Resource(
            id="res_7",
            name="St. Vincent de Paul Emergency Assistance",
            description="Catholic charity providing emergency rent, utilities, food",
            category=Category.RENT,
            eligibility_criteria="Documented emergency",
            max_amount=800,
            typical_approval_time="3-5 days",
            application_difficulty="easy",
            success_rate=0.70,
            contact_info="Local parish or svdpusa.org",
            location="National"
        ),
    ]
    RESOURCES_DB.extend(resources)

def seed_cases():
    """Add realistic employee cases"""
    now = datetime.now()
    
    # Case 1: Critical eviction case
    case1 = Case(
        id="case_1",
        employee_name="John Martinez",
        employer="Amazon Fulfillment Center",
        urgency=UrgencyLevel.CRITICAL,
        categories=[Category.RENT],
        last_contact=now,
        status="active",
        financial_snapshot={
            "annual_income": 35000,
            "credit_score": 580,
            "savings": 120,
            "total_debt": 8500,
            "dependents": 2
        },
        open_actions=[
            "Apply to Amazon Hardship Fund",
            "Contact landlord to negotiate",
            "Explore backup loan options"
        ],
        messages=[],
        sentiment=Sentiment.DESPERATE
    )
    
    msg1 = Message(
        id="msg_1",
        case_id="case_1",
        sender="employee",
        content="Hi Sarah, I'm really stressed. I'm $800 behind on rent and my landlord just gave me an eviction notice. I have until Friday to pay or I'm out. I have two kids and don't know what to do.",
        timestamp=now
    )
    case1.messages.append(msg1)
    CASES_DB["case_1"] = case1
    MESSAGES_DB.append(msg1)
    
    # Case 2: Medical debt
    case2 = Case(
        id="case_2",
        employee_name="Maria Chen",
        employer="Kaiser Permanente",
        urgency=UrgencyLevel.HIGH,
        categories=[Category.MEDICAL, Category.DEBT],
        last_contact=now - timedelta(hours=1),
        status="active",
        financial_snapshot={
            "annual_income": 52000,
            "credit_score": 640,
            "savings": 800,
            "total_debt": 12000,
            "dependents": 1
        },
        open_actions=[
            "Review Kaiser employee assistance",
            "Apply for hospital payment plan"
        ],
        messages=[],
        sentiment=Sentiment.ANXIOUS
    )
    CASES_DB["case_2"] = case2
    
    # Case 3: Transportation
    case3 = Case(
        id="case_3",
        employee_name="Tyrone Washington",
        employer="Walmart",
        urgency=UrgencyLevel.MEDIUM,
        categories=[Category.TRANSPORTATION],
        last_contact=now - timedelta(hours=2),
        status="active",
        financial_snapshot={
            "annual_income": 28000,
            "credit_score": 520,
            "savings": 50,
            "total_debt": 6000,
            "dependents": 0
        },
        open_actions=[
            "Research public transit subsidies",
            "Look into car repair programs"
        ],
        messages=[],
        sentiment=Sentiment.CALM
    )
    CASES_DB["case_3"] = case3
    
    # Case 4: Utilities
    case4 = Case(
        id="case_4",
        employee_name="Sarah Williams",
        employer="Target",
        urgency=UrgencyLevel.HIGH,
        categories=[Category.UTILITIES],
        last_contact=now - timedelta(hours=3),
        status="active",
        financial_snapshot={
            "annual_income": 31000,
            "credit_score": 610,
            "savings": 200,
            "total_debt": 4500,
            "dependents": 1
        },
        open_actions=[
            "Apply for PG&E CARE discount",
            "Set up payment plan"
        ],
        messages=[],
        sentiment=Sentiment.ANXIOUS
    )
    CASES_DB["case_4"] = case4
    
    # Case 5: Food insecurity
    case5 = Case(
        id="case_5",
        employee_name="Miguel Rodriguez",
        employer="Safeway",
        urgency=UrgencyLevel.MEDIUM,
        categories=[Category.FOOD],
        last_contact=now - timedelta(days=1),
        status="active",
        financial_snapshot={
            "annual_income": 29000,
            "credit_score": 550,
            "savings": 30,
            "total_debt": 5000,
            "dependents": 3
        },
        open_actions=[
            "Apply for CalFresh",
            "Connect with local food bank"
        ],
        messages=[],
        sentiment=Sentiment.CALM
    )
    CASES_DB["case_5"] = case5

def init_data():
    """Initialize all seed data"""
    seed_resources()
    seed_cases()