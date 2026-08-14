SITE = {
    "name": "Norman Hoang",
    "location": "New York, NY",
    "email": "normanhoang@gmail.com",
    "linkedin": "https://www.linkedin.com/in/normanhoang/",
    "github": "https://github.com/normanhoang/",
    "headline": "I build quantitative risk and pricing systems for banking.",
    "supporting_line": (
        "Quantitative Developer specializing in model implementation, regulatory "
        "analytics, and production-scale data engineering."
    ),
    "current_employer_line": (
        "Currently a Vice President in Global Risk Analytics at Bank of America."
    ),
    "repositories": {
        "finapp": "https://github.com/normanhoang/fin_app",
        "volatility_arbitrage": "https://github.com/normanhoang/cpp_final_project",
        "sp_1500_forecasting": "https://github.com/normanhoang/SVM_Analysis",
    },
}


PROOF_POINTS = (
    {
        "value": "~2 billion",
        "label": "market-data records processed daily",
        "detail": (
            "Distributed PySpark pipelines for equity order-book and trade data."
        ),
    },
    {
        "value": "58 → 119",
        "label": "users of the shared statistical library",
        "detail": "Adoption grew through Knowledge Shares and a user-driven roadmap.",
    },
    {
        "value": "IFRS · CECL · CCAR",
        "label": "risk processes supported by calibration outputs",
        "detail": "Reusable numerical and statistical routines for regulated work.",
    },
)


SKILL_GROUPS = (
    {
        "title": "Risk & regulatory analytics",
        "skills": (
            "Risk calibration",
            "IFRS",
            "CECL",
            "CCAR",
            "Loss forecasting",
        ),
        "evidence": "Financial Risk Calibration Library",
    },
    {
        "title": "Quantitative model implementation",
        "skills": (
            "Python",
            "NumPy",
            "Group Lasso",
            "LARS/LASSO",
            "Statistical modeling",
        ),
        "evidence": "Group Lasso Model Implementation and Runtime Optimization",
    },
    {
        "title": "Quant platform & data engineering",
        "skills": (
            "Spark/PySpark",
            "Python 3.12",
            "JupyterLab",
            "SQL/Trino",
            "Hadoop/Hive",
            "CI/CD",
        ),
        "evidence": (
            "Spark and Python Quant Platform Modernization; Oracle-to-Trino "
            "Pipeline Modernization"
        ),
    },
    {
        "title": "Risk & pricing technology",
        "skills": (
            "Derivatives",
            "Fixed income",
            "C++",
            "Computational finance",
            "Model explainability",
        ),
        "evidence": "Academic projects and independent research",
    },
)


EXPERIENCE = (
    {
        "employer": "Bank of America",
        "title": "Vice President, Quantitative Finance Analyst",
        "group": "Global Risk Analytics",
        "dates": "January 2023–present",
        "highlights": (
            "Primary technical owner of a shared Python statistical library used "
            "for model development, validation, execution, and monitoring; grew "
            "adoption from 58 to 119 users through Knowledge Shares, sustained "
            "support, and a user-driven roadmap.",
            "Led modernization of the library for Spark 3.5.6 and Python 3.12 and "
            "built a shared JupyterLab environment used by hundreds across the line "
            "of business during a collaborative 3–4 month rollout.",
            "Partnered across teams to add Hazard Rate, Beta, Trinomial, Inflated "
            "Beta, and Bayesian regression to the shared library.",
            "Develop improvements to risk calibration routines whose outputs support "
            "IFRS, CECL, and CCAR processes.",
            "Built distributed market-data and quality-control pipelines handling "
            "approximately 2 billion equity order-book and trade records daily.",
        ),
    },
    {
        "employer": "Bank of America",
        "title": "Assistant Vice President, Quantitative Finance Analyst",
        "group": "Global Risk Analytics",
        "dates": "August 2019–December 2022",
        "highlights": (
            "Programmed a Blockwise Coordinate Gradient Descent Group Lasso module "
            "for logistic and linear regression from research papers.",
            "Reduced regression runtime by 70% with vectorized NumPy algorithms on "
            "credit-card and mortgage benchmarks.",
            "Reduced custom-regression runtime by 60% with a MapReduce implementation "
            "of Nesterov Momentum on a one-billion-row dataset.",
            "Developed and tested loss-forecasting models for consumer-credit, "
            "auto-loan, and mortgage workflows.",
        ),
    },
    {
        "employer": "Extron Electronics",
        "title": "Senior Application Engineer",
        "group": "Control Systems Support",
        "dates": "September 2017–July 2019",
        "highlights": (
            "Trained more than 250 resellers and installers on Python-based control "
            "system programming software.",
            "Led control-system design integration across engineering teams for "
            "Fortune 500 conference-room installations.",
        ),
    },
    {
        "employer": "Extron Electronics",
        "title": "Application Engineer",
        "group": "Control Systems Support",
        "dates": "October 2012–September 2017",
        "highlights": (
            "Developed Python control and automation software for enterprise meeting "
            "spaces.",
            "Implemented SQL-based resource-management software for universities and "
            "large business campuses.",
        ),
    },
    {
        "employer": "Edwards Lifesciences",
        "title": "IT Technician",
        "location": "Irvine, CA",
        "dates": "August 2011–October 2012",
        "highlights": (
            "Built and configured PCs for new employees according to hardware and "
            "software requirements.",
            "Created CRM ticket-data visualizations by processing SQL Server "
            "information into business-intelligence software.",
        ),
    },
)


EDUCATION = (
    {
        "institution": "Fordham University",
        "degree": "M.S. in Quantitative Finance",
        "dates": "2018–2019",
        "coursework": (
            "Stochastic calculus",
            "Derivatives and fixed income",
            "Risk management",
            "Advanced C++",
            "Computational finance",
        ),
    },
    {
        "institution": "University of California, Irvine",
        "degree": (
            "B.S. in Electrical Engineering, Specialization in Systems and Signals"
        ),
        "dates": "2007–2012",
        "coursework": (),
    },
)


LEADERSHIP = (
    "Led the Global Risk Analytics Knowledge Share program for three years.",
    "Served as a member of the Jersey City Site Team.",
    "Founded and led the employee book club.",
)


ACADEMIC_PROJECTS = (
    {
        "title": "Algorithmic Trading Prototype",
        "description": (
            "Processed live equities, futures, and options feeds for concurrent order "
            "handling, with attention to latency and trade slippage."
        ),
        "repository": None,
    },
    {
        "title": "C++ Pricing and Risk Library",
        "description": (
            "Built reusable object-oriented pricing and risk components across "
            "equities, fixed income, and credit."
        ),
        "repository": None,
    },
    {
        "title": "Volatility-Arbitrage Strategy",
        "description": (
            "Compared implied volatility with GARCH forecasts and constructed a "
            "delta-neutral portfolio around identified spreads."
        ),
        "repository": "https://github.com/normanhoang/cpp_final_project",
    },
    {
        "title": "S&P 1500 Forecasting Model",
        "description": (
            "Combined regression-based ranking, data audit, SVM classification, and "
            "efficient-frontier position sizing."
        ),
        "repository": "https://github.com/normanhoang/SVM_Analysis",
    },
)


CREDENTIALS = (
    {"name": "C++ Programming", "issuer": "Baruch College"},
    {
        "name": "Statistical Thinking for Data Science and Analytics",
        "issuer": "Columbia University",
    },
    {
        "name": "Professional Program Certificate in Data Science",
        "issuer": "Microsoft",
    },
    {"name": "GitHub Foundations", "issuer": "GitHub"},
)


INDEPENDENT_WORK = (
    {
        "title": "FinApp",
        "kind": "iOS personal finance app",
        "description": (
            "A SwiftUI and SwiftData app with a secure, idempotent SimpleFin sync "
            "pipeline, TLS certificate pinning, biometric app lock, automated "
            "categorization, recurring-bill detection, and 11 unit-test suites. "
            "Claude Code assisted development; the architecture, security controls, "
            "tests, and engineering decisions are Norman's."
        ),
        "repository": "https://github.com/normanhoang/fin_app",
    },
    {
        "title": "Mathematics of Model Explainability",
        "kind": "Internal working paper",
        "description": (
            "An internal, non-peer-reviewed working paper for Model Risk Management "
            "covering XGBoost, SHAP, and feature importance."
        ),
        "repository": None,
    },
)


CASE_STUDIES = (
    {
        "slug": "risk-calibration",
        "title": "Financial Risk Calibration Library",
        "eyebrow": "Risk & regulatory analytics",
        "summary": (
            "Improving reusable calibration tooling whose outputs support IFRS, "
            "CECL, and CCAR risk processes."
        ),
        "sections": {
            "Context": (
                "Within Bank of America Global Risk Analytics, I contribute to an "
                "in-house financial risk calibration library used across regulated "
                "risk processes."
            ),
            "Problem": (
                "The library calibrates Default Rate Transition, Loss Given Default, "
                "Balance, NPA, TTR, and macrofactor moments. Those outputs need to "
                "remain consistent and reusable as they feed IFRS, CECL, and CCAR "
                "workflows."
            ),
            "Constraints": (
                "The work sits inside a shared banking platform with model-governance "
                "expectations and confidential data and implementation details. This "
                "public account therefore focuses on responsibilities and process, "
                "not internal parameters or controls."
            ),
            "Approach": (
                "I develop improvements to shared calibration routines and their "
                "reusable interfaces, with an emphasis on numerical consistency, "
                "verification, and maintainability for model-development and "
                "execution workflows."
            ),
            "Measurable impact": (
                "The resulting calibration outputs support three major accounting "
                "and stress-testing frameworks: IFRS, CECL, and CCAR."
            ),
        },
        "technologies": (
            "Python",
            "Numerical methods",
            "Statistical modeling",
            "Risk calibration",
        ),
    },
    {
        "slug": "spark-python-modernization",
        "title": "Spark and Python Quant Platform Modernization",
        "eyebrow": "Quant platform engineering",
        "summary": (
            "Modernizing shared quantitative tooling and the environment used to "
            "develop and run it across Global Risk Analytics."
        ),
        "sections": {
            "Context": (
                "As primary technical owner of a shared statistical library, I led "
                "its modernization for a new Python and Spark platform baseline."
            ),
            "Problem": (
                "The library needed full compliance with Spark 3.5.6 and Python "
                "3.12, together with a consistent environment for quantitative "
                "development across Global Risk Analytics."
            ),
            "Constraints": (
                "The rollout had to preserve continuity for downstream teams while "
                "shared libraries and environments changed. This public account "
                "therefore focuses on ownership and outcomes rather than internal "
                "infrastructure or incident details."
            ),
            "Approach": (
                "I led the library compliance work, built a shared JupyterLab "
                "environment, and collaborated with teams through hands-on support "
                "throughout the rollout."
            ),
            "Measurable impact": (
                "The modernization was delivered over 3–4 months, and the shared "
                "environment is now used by hundreds across the line of business."
            ),
        },
        "technologies": (
            "Python 3.12",
            "Spark 3.5.6",
            "PySpark",
            "JupyterLab",
            "CI/CD",
        ),
    },
    {
        "slug": "group-lasso",
        "title": "Group Lasso Model Implementation and Runtime Optimization",
        "eyebrow": "Model implementation & optimization",
        "summary": (
            "Research-to-production implementation of grouped regression methods "
            "with measured runtime improvements."
        ),
        "sections": {
            "Context": (
                "As an Assistant Vice President in Global Risk Analytics, I "
                "implemented quantitative regression tooling for consumer-credit, "
                "auto-loan, and mortgage modeling workflows."
            ),
            "Problem": (
                "The team needed Group Lasso support for logistic and linear "
                "regression, together with faster execution for custom algorithms "
                "operating on large credit datasets."
            ),
            "Constraints": (
                "The implementation had to translate multiple research papers into "
                "reliable Python while preserving model behavior across credit-card "
                "and mortgage benchmarks and distributed prediction workloads."
            ),
            "Approach": (
                "I programmed a Blockwise Coordinate Gradient Descent Group Lasso "
                "module from scratch, used vectorized NumPy algorithms for parallel "
                "SIMD calculations, and applied a MapReduce implementation of "
                "Nesterov Momentum to PySpark prediction models."
            ),
            "Measurable impact": (
                "Vectorization reduced total regression runtime by 70%. The MapReduce "
                "optimization reduced custom-regression runtime by 60% on a "
                "one-billion-row dataset."
            ),
        },
        "technologies": ("Python", "NumPy", "PySpark", "MapReduce", "Group Lasso"),
    },
    {
        "slug": "oracle-trino",
        "title": "Oracle-to-Trino Pipeline Modernization",
        "eyebrow": "Production-scale data engineering",
        "summary": (
            "Rebuilding an unreliable bulk extraction into a parallel, skew-aware "
            "pipeline for downstream analytics."
        ),
        "sections": {
            "Context": (
                "A recurring Oracle bulk-data pull supported downstream quantitative "
                "and analytics work but had become an operational bottleneck."
            ),
            "Problem": (
                "The extraction ran for more than 8 hours and failed repeatedly, "
                "making the delivery window unreliable."
            ),
            "Constraints": (
                "The source data was skewed across systems and time periods, and the "
                "output still needed to land in the existing Hadoop and Hive "
                "environment."
            ),
            "Approach": (
                "I co-designed the solution with the team, led the implementation, "
                "and wrote the code for a parallel Trino extraction chunked by source "
                "system and time period to control skew."
            ),
            "Measurable impact": (
                "The rebuilt pipeline cut runtime from more than 8 hours to 2 hours "
                "and eliminated the recurring failures."
            ),
        },
        "technologies": ("Python", "SQL", "Oracle", "Trino", "Hadoop", "Hive"),
    },
)


CASE_STUDIES_BY_SLUG = {study["slug"]: study for study in CASE_STUDIES}


def get_case_study(slug: str) -> dict | None:
    return CASE_STUDIES_BY_SLUG.get(slug)
