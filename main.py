import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from agents.enhancer import enhance_and_suggest
from agents.searcher import find_matching_jobs_from_resume
from agents.clusterer import cluster_jobs
from agents.interviewer import generate_interview_questions
from utils import load_file, write_file

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment() -> bool:
    """Check if all required environment variables are set"""
    logger.info("Checking environment configuration...")
    
    # Check for required API key
    api_key = os.getenv("METIS_API_KEY")
    if not api_key:
        logger.error("METIS_API_KEY not found in environment variables")
        logger.error("Please set your Metis.ai API key in the .env file")
        return False
    
    logger.info("Environment configuration looks good")
    return True

def safe_import():
    """Import all required modules with comprehensive error handling"""
    try:

        
        logger.info("Successfully imported all agent modules")
        
        return {
            'enhance_and_suggest': enhance_and_suggest,
            'search_jobs': find_matching_jobs_from_resume,
            'cluster_jobs': cluster_jobs,
            'generate_interview_questions': generate_interview_questions,
            'load_file': load_file,
            'write_file': write_file
        }
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please check that all dependencies are installed")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}")
        return None

def run_enhancement_pipeline(modules: Dict[str, Any], resume: str, job_desc: str, role: str) -> Dict[str, Any]:
    """Execute the resume enhancement pipeline with proper CSV integration"""
    
    results = {}
    
    # Step 1: Resume Enhancement and Gap Analysis
    logger.info("Starting resume enhancement and gap analysis...")
    try:
        enhancement_result = modules['enhance_and_suggest'](
            resume_text=resume,
            job_description=job_desc,
            target_role=role
        )
        results['enhancement'] = enhancement_result
        logger.info("Resume enhancement completed successfully")
        
        # Save enhancement results
        modules['write_file']("output/improved_resume.txt", enhancement_result.get("improved_resume", "Enhancement failed"))
        modules['write_file']("output/resume_gaps.txt", "\n".join(enhancement_result.get("gaps", ["No gaps identified"])))
        
    except Exception as e:
        logger.error(f"Resume enhancement failed: {e}")
        results['enhancement'] = {
            "improved_resume": resume,
            "gaps": [f"Enhancement error: {str(e)}"],
            "upskill_recommendations": {},
            "error": str(e)
        }
    
    # Step 2: Job Search with CSV Priority
    logger.info("Starting job search...")
    try:
        # Paths relative to main.py
        csv_path    = "../data/sample100.csv"
        resume_path = "../data/sample_resume.txt"

        # resume-based matching (no 'query' parameter any more)
        jobs = modules['search_jobs'](
            resume_path=resume_path,
            csv_path=csv_path,
            max_results=8
        )
        
        results['jobs'] = jobs
        logger.info(f"Found {len(jobs)} job opportunities")
        
        # Save job results
        import json
        modules['write_file']("output/jobs.json", json.dumps(jobs, indent=2))
        
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        results['jobs'] = []
        results['job_search_error'] = str(e)
    
    # Step 3: Job Clustering (only if we have jobs)
    if results.get('jobs'):
        logger.info("Starting job clustering...")
        try:
            clusters = modules['cluster_jobs'](jobs=results['jobs'], n_clusters=3)
            results['clusters'] = clusters
            logger.info(f"Created {len(clusters)} job clusters")
            
            # Save clustering results
            import json
            modules['write_file']("output/clusters.json", json.dumps(clusters, indent=2, default=str))
            
        except Exception as e:
            logger.error(f"Job clustering failed: {e}")
            results['clusters'] = {0: results['jobs']}
            results['clustering_error'] = str(e)
    else:
        logger.warning("Skipping clustering - no jobs available")
        results['clusters'] = {}
    
    # Step 4: Interview Question Generation
    if results.get('clusters'):
        logger.info("Generating interview questions...")
        try:
            questions = {}
            for cluster_id, cluster_jobs in results['clusters'].items():
                if cluster_jobs:
                    cluster_questions = modules['generate_interview_questions'](cluster_jobs)
                    questions[cluster_id] = cluster_questions
            
            results['interview_questions'] = questions
            logger.info(f"Generated interview questions for {len(questions)} clusters")
            
            # Save interview questions
            import json
            modules['write_file']("output/interview_questions.json", json.dumps(questions, indent=2))
            
        except Exception as e:
            logger.error(f"Interview question generation failed: {e}")
            results['interview_questions'] = {}
            results['interview_error'] = str(e)
    else:
        logger.warning("Skipping interview questions - no job clusters available")
        results['interview_questions'] = {}
    
    return results

def generate_summary_report(results: Dict[str, Any], role: str) -> str:
    """Generate comprehensive summary report"""
    from datetime import datetime
    
    report_lines = [
        f"Resume Enhancement Pipeline Report",
        f"=" * 50,
        f"Target Role: {role}",
        f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "PIPELINE EXECUTION SUMMARY:",
        ""
    ]
    
    # Enhancement Results
    enhancement = results.get('enhancement', {})
    if enhancement and not enhancement.get('error'):
        gaps_count = len(enhancement.get('gaps', []))
        recommendations_count = len(enhancement.get('upskill_recommendations', {}))
        report_lines.extend([
            f"✓ Resume Enhancement: SUCCESS", 
            f"  - Identified {gaps_count} skill gaps",
            f"  - Generated {recommendations_count} upskilling recommendations",
            ""
        ])
    else:
        report_lines.extend([
            f"✗ Resume Enhancement: FAILED",
            f"  - Error: {enhancement.get('error', 'Unknown error')}",
            ""
        ])
    
    # Job Search Results
    jobs = results.get('jobs', [])
    if jobs:
        report_lines.extend([
            f"✓ Job Search: SUCCESS",
            f"  - Found {len(jobs)} relevant job opportunities from CSV",
            f"  - Using local job database (no web scraping needed)",
            ""
        ])
    else:
        error = results.get('job_search_error', 'No jobs found')
        report_lines.extend([
            f"✗ Job Search: FAILED",
            f"  - Issue: {error}",
            f"  - Check that ../data/sample100.csv exists and is readable",
            ""
        ])
    
    # Clustering Results
    clusters = results.get('clusters', {})
    if clusters:
        report_lines.extend([
            f"✓ Job Clustering: SUCCESS",
            f"  - Organized jobs into {len(clusters)} strategic clusters",
            ""
        ])
    else:
        report_lines.extend([
            f"✗ Job Clustering: SKIPPED",
            f"  - Reason: Insufficient job data",
            ""
        ])
    
    # Interview Questions
    questions = results.get('interview_questions', {})
    if questions:
        total_questions = sum(len(q_list) for q_list in questions.values())
        report_lines.extend([
            f"✓ Interview Preparation: SUCCESS",
            f"  - Generated {total_questions} tailored interview questions",
            ""
        ])
    else:
        report_lines.extend([
            f"✗ Interview Preparation: SKIPPED",
            f"  - Reason: No job clusters available",
            ""
        ])
    
    report_lines.extend([
        "NEXT STEPS:",
        "1. Review the improved resume in output/improved_resume.txt",
        "2. Check identified skill gaps in output/resume_gaps.txt", 
        "3. Explore job opportunities in output/jobs.json",
        "4. Practice with interview questions in output/interview_questions.json",
        "",
        "All output files are saved in the 'output' directory.",
        ""
    ])
    
    return "\n".join(report_lines)

def main():
    """Main execution function with proper error handling"""
    
    logger.info("Starting Resume Hunter Agent Pipeline")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Environment check
    if not check_environment():
        sys.exit(1)
    
    # Import modules
    modules = safe_import()
    if not modules:
        sys.exit(1)
    
    # Load input data with correct paths
    try:
        logger.info("Loading input data...")
        resume = modules['load_file']("../data/sample_resume.txt")
        # You might not have sample_hiring.txt based on your directory structure
        # So let's make this more flexible
        try:
            job_desc = modules['load_file']("../data/sample_hiring.txt")
        except:
            # Create a generic job description if file doesn't exist
            job_desc = "Looking for a Machine Learning Engineer with experience in Python, ML algorithms, and data analysis."
            logger.warning("sample_hiring.txt not found, using generic job description")
        
        role = "Machine Learning Engineer"
        
        logger.info(f"Loaded resume ({len(resume)} characters)")
        logger.info(f"Loaded job description ({len(job_desc)} characters)")
        
    except Exception as e:
        logger.error(f"Failed to load input data: {e}")
        sys.exit(1)
    
    # Execute pipeline
    try:
        results = run_enhancement_pipeline(modules, resume, job_desc, role)
        
        # Generate and save summary
        summary_report = generate_summary_report(results, role)
        modules['write_file']("output/pipeline_summary.txt", summary_report)
        
        # Display summary
        print("\n" + summary_report)
        
        logger.info("Pipeline execution completed successfully")
        logger.info("Check the 'output' directory for all generated files")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        print(f"\nPipeline failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
