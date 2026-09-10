"""Seed data source.

Contains ~40 realistic demo internship records that exercise every
filter, eligibility state, and compensation type. Records use fictional
company names or clearly-labeled demo listings. They are NOT real job postings.

Records are marked is_seed=True so they can be identified and replaced later.
"""
from datetime import datetime, timedelta, timezone

from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    InternshipType,
)
from app.schemas.internship import InternshipCreate
from app.scrapers.base import InternshipSource


def _dt(days_ago: int) -> datetime:
    """Return a naive UTC datetime N days before now."""
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(tzinfo=None)


def _deadline(days_from_now: int) -> datetime:
    return (datetime.now(timezone.utc) + timedelta(days=days_from_now)).replace(tzinfo=None)


SEED_INTERNSHIPS: list[dict] = [
    # ------------------------------------------------------------------ #
    # LIKELY ELIGIBLE — explicitly India / APAC / global                  #
    # ------------------------------------------------------------------ #
    {
        "title": "Software Engineering Intern",
        "company_name": "ByteForge Labs",
        "company_url": "https://byteforge.example.com",
        "description": (
            "ByteForge Labs is looking for a passionate Software Engineering Intern to join our "
            "fully distributed team. This is a remote internship open to candidates based in India. "
            "You will work on our core platform using Python and FastAPI, write tests, review pull "
            "requests, and participate in sprint planning. Great opportunity to learn production "
            "engineering in a fast-paced startup environment."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/byteforge-swe-intern",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 20000,
        "salary_max": 35000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "FastAPI", "PostgreSQL", "Git", "Docker"],
        "tags": ["backend", "startup", "internship"],
        "posted_at": _dt(2),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Backend Engineering Intern (Python)",
        "company_name": "NimbusTech",
        "company_url": "https://nimbustech.example.io",
        "description": (
            "NimbusTech is a Singapore-based SaaS company building cloud infrastructure tools. "
            "We are hiring a Backend Engineering Intern who can work remotely from India or Singapore. "
            "You'll work with our Python/Django backend, contribute to REST APIs, and help improve "
            "our CI/CD pipelines. Stipend provided. Duration: 3 months."
        ),
        "source": "Internshala",
        "source_url": "https://internshala.example.com/jobs/nimbustech-backend",
        "location": "Remote – India / Singapore",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 25000,
        "salary_max": 40000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Django", "REST API", "Docker", "Git"],
        "tags": ["backend", "singapore", "saas"],
        "posted_at": _dt(5),
        "deadline": _deadline(25),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Full Stack Developer Intern",
        "company_name": "Crestwave Digital",
        "company_url": "https://crestwave.example.com",
        "description": (
            "Crestwave Digital is an Indian product company building e-commerce solutions. "
            "We are looking for a Full Stack Developer Intern to join our growing team. "
            "You'll build features across our React frontend and Node.js/Express backend. "
            "This is a paid remote internship for students based in India."
        ),
        "source": "Unstop",
        "source_url": "https://unstop.example.com/jobs/crestwave-fullstack",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 15000,
        "salary_max": 25000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["JavaScript", "React", "Node.js", "SQL", "Git"],
        "tags": ["fullstack", "ecommerce", "india"],
        "posted_at": _dt(1),
        "deadline": _deadline(20),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Machine Learning Engineering Intern",
        "company_name": "Axiom AI",
        "company_url": "https://axiom-ai.example.com",
        "description": (
            "Axiom AI is building the next generation of production ML systems. "
            "We are hiring an ML Engineering Intern who will work on data pipelines, "
            "model training infrastructure, and evaluation frameworks using Python. "
            "Remote internship, open to candidates in India. Prior ML coursework required."
        ),
        "source": "Company Careers",
        "source_url": "https://axiom-ai.example.com/careers/ml-intern",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 30000,
        "salary_max": 50000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Machine Learning", "PyTorch", "Data Engineering", "Git"],
        "tags": ["ml", "ai", "engineering"],
        "posted_at": _dt(3),
        "deadline": _deadline(14),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "DevOps / Cloud Engineering Intern",
        "company_name": "Stratum Cloud",
        "company_url": "https://stratumcloud.example.com",
        "description": (
            "Stratum Cloud is a cloud-native infrastructure company. We are looking for a "
            "DevOps / Cloud Engineering Intern to help manage our Kubernetes clusters and CI/CD "
            "pipelines on AWS. The role is fully remote and open to students in India. "
            "You will get hands-on experience with Docker, Terraform, and GitHub Actions."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/stratum-devops",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 20000,
        "salary_max": 30000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Docker", "Kubernetes", "AWS", "Git", "Python"],
        "tags": ["devops", "cloud", "infrastructure"],
        "posted_at": _dt(7),
        "deadline": _deadline(21),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Android Development Intern",
        "company_name": "Mobilify",
        "company_url": "https://mobilify.example.app",
        "description": (
            "Mobilify is a mobile-first startup building apps for the Indian market. "
            "We're hiring an Android Development Intern to work on our flagship app using "
            "Kotlin. You'll implement new features, fix bugs, and write unit tests. "
            "Remote — open to candidates in India. Stipend: ₹18,000/month."
        ),
        "source": "Internshala",
        "source_url": "https://internshala.example.com/jobs/mobilify-android",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 18000,
        "salary_max": 18000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Kotlin", "Android", "Java", "Git"],
        "tags": ["mobile", "android", "india"],
        "posted_at": _dt(4),
        "deadline": _deadline(18),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "C++ Systems Programming Intern",
        "company_name": "Ironclad Systems",
        "company_url": "https://ironclad.example.com",
        "description": (
            "Ironclad Systems builds low-latency trading infrastructure. We have an opening for a "
            "C++ Systems Programming Intern. You will contribute to our matching engine and latency "
            "benchmarking tools. Remote from APAC — includes India. Strong C++ fundamentals required."
        ),
        "source": "Company Careers",
        "source_url": "https://ironclad.example.com/careers/cpp-intern",
        "location": "Remote – APAC",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 40000,
        "salary_max": 60000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["C++", "C", "Systems", "Git"],
        "tags": ["systems", "low-latency", "cpp"],
        "posted_at": _dt(6),
        "deadline": _deadline(28),
        "is_active": True,
        "is_seed": True,
    },

    # ------------------------------------------------------------------ #
    # UNCLEAR ELIGIBILITY — worldwide / global / no restriction stated     #
    # ------------------------------------------------------------------ #
    {
        "title": "Software Engineer Intern (Go)",
        "company_name": "PulseDB",
        "company_url": "https://pulsedb.example.com",
        "description": (
            "PulseDB is an open-source database company. We hire interns worldwide for our "
            "distributed systems team. You'll work on our Go-based storage engine, write tests, "
            "and contribute to our open-source codebase. 100% remote, work from anywhere."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/pulsedb-go-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.SUMMER,
        "compensation_type": CompensationType.PAID,
        "salary_min": 3000,
        "salary_max": 5000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Go", "Distributed Systems", "SQL", "Git"],
        "tags": ["database", "go", "open-source"],
        "posted_at": _dt(8),
        "deadline": _deadline(22),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Rust Systems Intern",
        "company_name": "Ferrite Labs",
        "company_url": "https://ferra-labs.example.com",
        "description": (
            "Ferrite Labs builds memory-safe systems software in Rust. We are hiring a Rust Systems "
            "Intern to work on our WebAssembly runtime. This is a fully remote position with no "
            "geographic restriction — we have team members across 12 countries. "
            "Duration: 3 months. Paid internship."
        ),
        "source": "Company Careers",
        "source_url": "https://ferra-labs.example.com/careers/rust-intern",
        "location": "Remote – Global",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 2500,
        "salary_max": 4000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Rust", "Systems", "WebAssembly", "Git"],
        "tags": ["rust", "wasm", "systems"],
        "posted_at": _dt(10),
        "deadline": _deadline(35),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Frontend Engineering Intern (React / TypeScript)",
        "company_name": "Lumos UI",
        "company_url": "https://lumos-ui.example.com",
        "description": (
            "Lumos UI is a design-system company. We're looking for a Frontend Engineering Intern "
            "to build React components and write Storybook documentation. "
            "Fully remote, international team. No location requirements. Stipend: $1,500/month."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/lumos-ui-fe-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.PART_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 1500,
        "salary_max": 1500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["JavaScript", "TypeScript", "React", "CSS", "Git"],
        "tags": ["frontend", "design-system", "react"],
        "posted_at": _dt(12),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Data Engineering Intern",
        "company_name": "Cascade Analytics",
        "company_url": "https://cascade.example.com",
        "description": (
            "Cascade Analytics is a data platform company. We are hiring a Data Engineering Intern "
            "to help build our ETL pipelines and data warehouse infrastructure using Python and SQL. "
            "Work from anywhere — fully remote, international company."
        ),
        "source": "LinkedIn",
        "source_url": "https://linkedin.example.com/jobs/cascade-data-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 2000,
        "salary_max": 3500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "SQL", "Data Engineering", "AWS", "Git"],
        "tags": ["data", "etl", "analytics"],
        "posted_at": _dt(9),
        "deadline": _deadline(20),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Python Backend Intern",
        "company_name": "OpenRoute",
        "company_url": "https://openroute.example.io",
        "description": (
            "OpenRoute is building API infrastructure for the logistics industry. "
            "We're hiring a Python Backend Intern to help develop new API endpoints using FastAPI "
            "and PostgreSQL. Fully remote with async communication. We welcome applicants globally."
        ),
        "source": "Cutshort",
        "source_url": "https://cutshort.example.io/jobs/openroute-python-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 1800,
        "salary_max": 2800,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        "tags": ["backend", "api", "logistics"],
        "posted_at": _dt(14),
        "deadline": _deadline(28),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Summer Software Engineering Intern",
        "company_name": "Vortex Software",
        "company_url": "https://vortex.example.com",
        "description": (
            "Vortex Software is a VC-backed productivity startup. Our summer internship program "
            "is open to students worldwide. You'll work on core product features, write production "
            "code in Python and TypeScript, and present your work at the end of the program. "
            "Paid. Duration: 10 weeks."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/vortex-summer-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.SUMMER,
        "compensation_type": CompensationType.PAID,
        "salary_min": 4000,
        "salary_max": 6000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "TypeScript", "SQL", "Git"],
        "tags": ["summer", "intern", "startup"],
        "posted_at": _dt(3),
        "deadline": _deadline(40),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Java Backend Engineering Intern",
        "company_name": "Hexagon Platform",
        "company_url": "https://hexagon.example.com",
        "description": (
            "Hexagon Platform builds enterprise software for supply chain management. "
            "We are hiring a Java Backend Engineering Intern to work on our Spring Boot microservices. "
            "Remote-first company with no geographic restrictions. Competitive stipend."
        ),
        "source": "Internshala",
        "source_url": "https://internshala.example.com/jobs/hexagon-java-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 20000,
        "salary_max": 35000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Java", "Spring Boot", "SQL", "Docker", "Git"],
        "tags": ["java", "backend", "enterprise"],
        "posted_at": _dt(11),
        "deadline": _deadline(25),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "iOS Development Intern (Swift)",
        "company_name": "Neon Apps",
        "company_url": "https://neon-apps.example.com",
        "description": (
            "Neon Apps is a consumer app company with products used by 5M+ users. "
            "We're hiring an iOS Development Intern to work on our flagship iOS app in Swift. "
            "Fully remote, international team — we work asynchronously across time zones."
        ),
        "source": "Company Careers",
        "source_url": "https://neon-apps.example.com/careers/ios-intern",
        "location": "Remote – Global",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 2500,
        "salary_max": 4000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Swift", "iOS", "Xcode", "Git"],
        "tags": ["mobile", "ios", "swift"],
        "posted_at": _dt(15),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Open Source Contributor Intern (Python / Rust)",
        "company_name": "Foundry OSS",
        "company_url": "https://foundryoss.example.org",
        "description": (
            "Foundry OSS is a nonprofit building developer tools. We run a paid open-source "
            "internship program for students worldwide. You'll contribute to Python and Rust "
            "projects used by thousands of developers. Fully remote, async, location-agnostic."
        ),
        "source": "Company Careers",
        "source_url": "https://foundryoss.example.org/internships/2026",
        "location": "Remote – Anywhere",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.PART_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 800,
        "salary_max": 1200,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Rust", "Git", "Open Source"],
        "tags": ["oss", "open-source", "nonprofit"],
        "posted_at": _dt(20),
        "deadline": _deadline(45),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Cloud Infrastructure Intern (AWS / GCP)",
        "company_name": "AetherScale",
        "company_url": "https://aetherscale.example.com",
        "description": (
            "AetherScale provides multi-cloud cost optimization tools. Our Cloud Infrastructure "
            "Intern will help manage our AWS and GCP environments, write Terraform modules, and "
            "build monitoring dashboards. Fully remote. We are an international team and welcome "
            "students from all countries."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/aetherscale-cloud-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 2000,
        "salary_max": 3500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["AWS", "GCP", "Docker", "Kubernetes", "Python", "Terraform"],
        "tags": ["cloud", "infra", "devops"],
        "posted_at": _dt(6),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Winter Intern – Systems & Infrastructure",
        "company_name": "Glacial Computing",
        "company_url": "https://glacial.example.com",
        "description": (
            "Glacial Computing is building a distributed file storage system in C and C++. "
            "Our winter internship program is open to students globally. You'll work on the "
            "network layer of our storage engine. Strong C/C++ knowledge required. Remote."
        ),
        "source": "Company Careers",
        "source_url": "https://glacial.example.com/careers/winter-intern",
        "location": "Remote – Global",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.WINTER,
        "compensation_type": CompensationType.PAID,
        "salary_min": 3000,
        "salary_max": 5000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["C", "C++", "Systems", "Networking", "Git"],
        "tags": ["systems", "storage", "winter", "cpp"],
        "posted_at": _dt(18),
        "deadline": _deadline(60),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Software Engineering Intern – No Experience Required",
        "company_name": "Launchpad Dev",
        "company_url": "https://launchpaddev.example.com",
        "description": (
            "Launchpad Dev is a coding bootcamp company that hires beginner-friendly interns. "
            "No prior internship experience needed. You will work on real projects using JavaScript "
            "and Python. Fully remote, open to students globally. Unpaid but comes with mentorship "
            "and a strong letter of recommendation."
        ),
        "source": "Internshala",
        "source_url": "https://internshala.example.com/jobs/launchpad-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.PART_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.UNPAID,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "salary_period": None,
        "experience_min": 0,
        "experience_max": 0,
        "skills": ["JavaScript", "Python", "Git"],
        "tags": ["beginner", "entry-level", "unpaid"],
        "posted_at": _dt(25),
        "deadline": _deadline(35),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Machine Learning Research Intern",
        "company_name": "Synthesis AI",
        "company_url": "https://synthesis-ai.example.com",
        "description": (
            "Synthesis AI is a research-focused AI lab. We are hiring a Machine Learning Research "
            "Intern to work on LLM evaluation benchmarks. You'll write Python code, run experiments, "
            "and co-author a technical report. PhD or final-year undergrad preferred. "
            "Compensation: research stipend. Remote from anywhere."
        ),
        "source": "Company Careers",
        "source_url": "https://synthesis-ai.example.com/research/intern-2026",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 3500,
        "salary_max": 6000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 2,
        "skills": ["Python", "Machine Learning", "PyTorch", "Data Engineering"],
        "tags": ["research", "ml", "llm", "ai"],
        "posted_at": _dt(7),
        "deadline": _deadline(20),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Backend Infrastructure Intern (Node.js / TypeScript)",
        "company_name": "Trident API",
        "company_url": "https://trident-api.example.com",
        "description": (
            "Trident API is building developer infrastructure for event-driven architectures. "
            "We are hiring a Backend Infrastructure Intern to work on our Node.js TypeScript codebase. "
            "Tasks include building webhook delivery systems and improving API observability. "
            "Remote, no location restrictions. Paid internship, $2,200/month."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/trident-api-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 2200,
        "salary_max": 2200,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Node.js", "TypeScript", "JavaScript", "Docker", "AWS"],
        "tags": ["backend", "api", "infra"],
        "posted_at": _dt(16),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Embedded Systems Intern (C / RTOS)",
        "company_name": "Quark Embedded",
        "company_url": "https://quark-emb.example.com",
        "description": (
            "Quark Embedded builds firmware for IoT devices. We are looking for an Embedded "
            "Systems Intern who is comfortable with C and RTOS. You will write firmware for "
            "our sensor modules and create automated test scripts in Python. "
            "Remote-first. Open globally."
        ),
        "source": "Company Careers",
        "source_url": "https://quark-emb.example.com/jobs/embedded-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 1800,
        "salary_max": 3000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["C", "RTOS", "Embedded", "Python", "Git"],
        "tags": ["embedded", "iot", "firmware", "c"],
        "posted_at": _dt(22),
        "deadline": _deadline(40),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Summer Internship – SRE / Platform Engineering",
        "company_name": "GridLine",
        "company_url": "https://gridline.example.com",
        "description": (
            "GridLine provides SaaS analytics for energy companies. Our summer SRE/Platform "
            "Engineering Internship is open to candidates worldwide. You will work on Kubernetes "
            "operators, incident response tooling, and our internal developer platform. "
            "100% remote. Duration: 12 weeks."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/gridline-sre-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.SUMMER,
        "compensation_type": CompensationType.PAID,
        "salary_min": 4000,
        "salary_max": 5500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Kubernetes", "Docker", "Python", "AWS", "Go"],
        "tags": ["sre", "platform", "summer", "devops"],
        "posted_at": _dt(5),
        "deadline": _deadline(55),
        "is_active": True,
        "is_seed": True,
    },

    # ------------------------------------------------------------------ #
    # UNLIKELY ELIGIBLE — US-only / requires work authorization            #
    # ------------------------------------------------------------------ #
    {
        "title": "Software Engineering Intern – Summer 2026",
        "company_name": "Polaris Tech",
        "company_url": "https://polaris.example.com",
        "description": (
            "Polaris Tech is a US-based fintech company. We are hiring Software Engineering Interns "
            "for our Summer 2026 program. Candidates must be located in the United States for the "
            "duration of the internship. US work authorization required. This is a hybrid role "
            "based in our New York and San Francisco offices."
        ),
        "source": "LinkedIn",
        "source_url": "https://linkedin.example.com/jobs/polaris-swe-intern",
        "location": "Remote – US Only",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNLIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.SUMMER,
        "compensation_type": CompensationType.PAID,
        "salary_min": 6000,
        "salary_max": 8000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Java", "SQL", "Git"],
        "tags": ["summer", "us-only", "fintech"],
        "posted_at": _dt(3),
        "deadline": _deadline(25),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Backend Engineering Intern",
        "company_name": "Meridian Cloud",
        "company_url": "https://meridian.example.cloud",
        "description": (
            "Meridian Cloud is a Series B cloud infrastructure company. Our remote internship "
            "program is open to candidates who can work remotely within the United States only. "
            "Candidates must have valid US work authorization. "
            "Strong Python and Kubernetes skills preferred."
        ),
        "source": "Company Careers",
        "source_url": "https://meridian.example.cloud/careers/intern-backend",
        "location": "Remote within the United States",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNLIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 5500,
        "salary_max": 7000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Kubernetes", "AWS", "Go"],
        "tags": ["backend", "us-only", "cloud"],
        "posted_at": _dt(8),
        "deadline": _deadline(20),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Machine Learning Engineering Intern",
        "company_name": "CognitionAI",
        "company_url": "https://cognition-ai.example.com",
        "description": (
            "CognitionAI is a well-funded AI research lab. Our ML Engineering Intern will work "
            "on training infrastructure and evaluation pipelines. Candidates must be US citizens "
            "or permanent residents. Remote within North America."
        ),
        "source": "LinkedIn",
        "source_url": "https://linkedin.example.com/jobs/cognition-ml-intern",
        "location": "Remote – North America",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNLIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.SUMMER,
        "compensation_type": CompensationType.PAID,
        "salary_min": 7000,
        "salary_max": 9000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Machine Learning", "PyTorch", "AWS"],
        "tags": ["ml", "ai", "us-only", "north-america"],
        "posted_at": _dt(4),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },

    # ------------------------------------------------------------------ #
    # ADDITIONAL VARIETY                                                   #
    # ------------------------------------------------------------------ #
    {
        "title": "Flutter Mobile Development Intern",
        "company_name": "Prism Apps",
        "company_url": "https://prism-apps.example.com",
        "description": (
            "Prism Apps is building cross-platform mobile apps using Flutter and Dart. "
            "We're hiring a Mobile Development Intern to work on our consumer fintech app. "
            "Remote — open to candidates in India and Southeast Asia. "
            "Stipend: ₹22,000/month."
        ),
        "source": "Internshala",
        "source_url": "https://internshala.example.com/jobs/prism-flutter",
        "location": "Remote – India / South Asia",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 22000,
        "salary_max": 22000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Flutter", "Dart", "Android", "iOS", "Git"],
        "tags": ["mobile", "flutter", "fintech", "india"],
        "posted_at": _dt(13),
        "deadline": _deadline(30),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Security Engineering Intern",
        "company_name": "VaultShield",
        "company_url": "https://vaultshield.example.com",
        "description": (
            "VaultShield builds security tooling for enterprise customers. We're hiring a "
            "Security Engineering Intern to work on vulnerability scanning tools in Python and Go. "
            "Fully remote. Open to students globally. Prior CTF experience is a plus."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/vaultshield-security",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 2000,
        "salary_max": 3500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Go", "Security", "Git"],
        "tags": ["security", "vulnerability", "ctf"],
        "posted_at": _dt(19),
        "deadline": _deadline(40),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Database Internship (PostgreSQL / Go)",
        "company_name": "DataTree",
        "company_url": "https://datatree.example.com",
        "description": (
            "DataTree is building a developer-friendly managed database service. "
            "We're looking for a Database Intern with interest in PostgreSQL internals and Go. "
            "You'll work on backup/restore tooling and connection pooling. Remote from anywhere. "
            "Compensation details available after screening."
        ),
        "source": "Company Careers",
        "source_url": "https://datatree.example.com/jobs/db-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.UNKNOWN,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "salary_period": None,
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Go", "PostgreSQL", "SQL", "Docker"],
        "tags": ["database", "go", "postgres"],
        "posted_at": _dt(30),
        "deadline": None,
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "AI/ML Infrastructure Intern",
        "company_name": "QuantumLeap ML",
        "company_url": "https://quantumleap-ml.example.com",
        "description": (
            "QuantumLeap ML is developing scalable training infrastructure for large language models. "
            "We're hiring an AI/ML Infrastructure Intern to help with distributed training jobs on "
            "GPU clusters using Python and CUDA. Remote — candidates in India encouraged to apply."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/quantumleap-ml-infra",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 35000,
        "salary_max": 55000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 2,
        "skills": ["Python", "Machine Learning", "AWS", "Docker", "CUDA"],
        "tags": ["ai", "ml", "infra", "llm", "gpu"],
        "posted_at": _dt(2),
        "deadline": _deadline(21),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Compiler Engineering Intern (LLVM / C++)",
        "company_name": "Bytecode Research",
        "company_url": "https://bytecode-research.example.com",
        "description": (
            "Bytecode Research is developing a next-generation compiler toolchain based on LLVM. "
            "Our Compiler Engineering Internship is open to students who have studied compilers, "
            "PL theory, or systems programming. C++ experience is required. Remote from anywhere."
        ),
        "source": "Company Careers",
        "source_url": "https://bytecode-research.example.com/careers/compiler-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 3000,
        "salary_max": 5000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 2,
        "skills": ["C++", "LLVM", "Compilers", "C", "Systems"],
        "tags": ["compiler", "llvm", "cpp", "systems"],
        "posted_at": _dt(17),
        "deadline": _deadline(45),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Part-Time Frontend Intern (Vue.js)",
        "company_name": "Mosaic Studio",
        "company_url": "https://mosaic-studio.example.com",
        "description": (
            "Mosaic Studio is a design-focused web agency. We are hiring a Part-Time Frontend "
            "Intern to help build client websites using Vue.js and CSS. Flexible hours, fully "
            "remote, international team. Great for students who want to balance academics and work."
        ),
        "source": "Cutshort",
        "source_url": "https://cutshort.example.io/jobs/mosaic-vue-intern",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.PART_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 800,
        "salary_max": 1500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["JavaScript", "Vue.js", "CSS", "HTML", "Git"],
        "tags": ["frontend", "part-time", "agency", "vue"],
        "posted_at": _dt(23),
        "deadline": None,
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Infrastructure / SRE Intern",
        "company_name": "Titan Platform",
        "company_url": "https://titan-platform.example.com",
        "description": (
            "Titan Platform is a B2B SaaS company. Our SRE Intern will help maintain our "
            "AWS infrastructure, write runbooks, and improve our observability stack. "
            "Candidates in India are welcome to apply for this remote role. "
            "Paid internship: ₹28,000/month."
        ),
        "source": "Unstop",
        "source_url": "https://unstop.example.com/jobs/titan-sre-intern",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 28000,
        "salary_max": 28000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["AWS", "Docker", "Python", "Kubernetes", "Git"],
        "tags": ["sre", "infra", "india", "devops"],
        "posted_at": _dt(9),
        "deadline": _deadline(28),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "React Native Mobile Intern",
        "company_name": "Crux Mobile",
        "company_url": "https://crux-mobile.example.com",
        "description": (
            "Crux Mobile is building a productivity app for remote teams. We need a React Native "
            "Mobile Intern to help ship features for our iOS and Android app. "
            "Remote from anywhere — we are an async-first team. No prior internship required."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/crux-rn-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 1500,
        "salary_max": 2500,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["JavaScript", "React", "React Native", "TypeScript", "Git"],
        "tags": ["mobile", "react-native", "async"],
        "posted_at": _dt(21),
        "deadline": _deadline(40),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Backend Intern – Flask / Python",
        "company_name": "Kestrel API",
        "company_url": "https://kestrel-api.example.com",
        "description": (
            "Kestrel API is a bootstrapped startup building API management tools. "
            "We need a Backend Intern comfortable with Python and Flask. "
            "You'll build new API endpoints, write integration tests, and help with documentation. "
            "Remote from India. Stipend: ₹15,000/month."
        ),
        "source": "Internshala",
        "source_url": "https://internshala.example.com/jobs/kestrel-flask",
        "location": "Remote – India",
        "remote": True,
        "india_eligibility": IndiaEligibility.LIKELY,
        "employment_type": EmploymentType.PART_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 15000,
        "salary_max": 15000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Python", "Flask", "SQL", "Git"],
        "tags": ["backend", "flask", "india", "api"],
        "posted_at": _dt(28),
        "deadline": _deadline(14),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Compiler / PL Research Intern (Haskell / OCaml)",
        "company_name": "Semaphore Research",
        "company_url": "https://semaphore-research.example.edu",
        "description": (
            "Semaphore Research is a university spinout studying type systems and compiler correctness. "
            "We offer a research internship for students with strong PL background (Haskell, OCaml, "
            "or similar). Fully remote. Open to students globally. Unpaid but provides research credit."
        ),
        "source": "Company Careers",
        "source_url": "https://semaphore-research.example.edu/internships/pl-intern",
        "location": "Remote – Worldwide",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.PART_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.UNPAID,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "salary_period": None,
        "experience_min": 0,
        "experience_max": 2,
        "skills": ["Haskell", "OCaml", "Compilers", "Git"],
        "tags": ["research", "pl", "compilers", "academic"],
        "posted_at": _dt(35),
        "deadline": None,
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "Site Reliability Engineering Intern",
        "company_name": "Aurora Systems",
        "company_url": "https://aurora-sys.example.com",
        "description": (
            "Aurora Systems provides managed Kubernetes infrastructure. We're looking for an SRE Intern "
            "to work on alerting systems and runbook automation. Candidates must be US citizens or "
            "hold a valid work authorization. Remote within the US only."
        ),
        "source": "Company Careers",
        "source_url": "https://aurora-sys.example.com/careers/sre-intern",
        "location": "Remote within the United States",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNLIKELY,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 5000,
        "salary_max": 7000,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["Kubernetes", "Python", "AWS", "Docker"],
        "tags": ["sre", "us-only", "cloud"],
        "posted_at": _dt(10),
        "deadline": _deadline(25),
        "is_active": True,
        "is_seed": True,
    },
    {
        "title": "GraphQL / API Engineering Intern",
        "company_name": "Lattice APIs",
        "company_url": "https://lattice-apis.example.com",
        "description": (
            "Lattice APIs is building a unified API gateway. We need a GraphQL / API Engineering Intern "
            "to help develop our schema federation layer in TypeScript and Node.js. "
            "Remote, international team. No location restrictions. Paid: $1,800/month."
        ),
        "source": "Wellfound",
        "source_url": "https://wellfound.example.com/jobs/lattice-graphql",
        "location": "Remote",
        "remote": True,
        "india_eligibility": IndiaEligibility.UNCLEAR,
        "employment_type": EmploymentType.FULL_TIME,
        "internship_type": InternshipType.GENERAL,
        "compensation_type": CompensationType.PAID,
        "salary_min": 1800,
        "salary_max": 1800,
        "salary_currency": "USD",
        "salary_period": "monthly",
        "experience_min": 0,
        "experience_max": 1,
        "skills": ["TypeScript", "Node.js", "GraphQL", "JavaScript", "Docker"],
        "tags": ["graphql", "api", "node"],
        "posted_at": _dt(26),
        "deadline": _deadline(35),
        "is_active": True,
        "is_seed": True,
    },
]


class SeedSource(InternshipSource):
    """Returns pre-defined seed/demo internships for initial database population."""

    source_name = "Seed Data"

    def fetch(self) -> list[InternshipCreate]:
        return [InternshipCreate(**record) for record in SEED_INTERNSHIPS]
