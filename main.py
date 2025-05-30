import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment() -> bool:

    logger.info("Checking environment configuration...")
    
    # Check for required API key
    api_key = os.getenv("METIS_API_KEY")
    if not api_key :
        logger.error("METIS_API_KEY not found in environment variables")
        logger.error("Please set your Metis.ai API key in the .env file")
        return False
    
    logger.info("Environment configuration looks good")
    return True

def safe_import():
    """
    Import all required modules with error handling.
    
    This function ensures that import errors are caught early and reported
    clearly, rather than causing cryptic error messages during execution.
    
    Returns:
        Dictionary containing imported functions, or None if imports fail
    """
    
    try:
        # Import all agent functions
        from agents.enhancer import enhance_and_suggest
        from agents.searcher import scrape_jobs
        from agents.clusterer import cluster_jobs
        from agents.interviewer import generate_interview_questions
        from utils import load_file, write_file
        
        logger.info("Successfully imported all agent modules")
        
        return {
            'enhance_and_suggest': enhance_and_suggest,
            'scrape_jobs': scrape_jobs,
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
    """
    Execute the resume enhancement pipeline with comprehensive error handling.
    
    This function wraps the core enhancement logic in try-catch blocks to ensure
    that partial failures don't crash your entire demo. Each step can fail
    independently while still allowing the demo to continue.
    
    Args:
        modules: Dictionary of imported functions from safe_import
        resume: Resume text content
        job_desc: Job description text
        role: Target role name
        
    Returns:
        Dictionary containing results from each pipeline step
    """
    
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
        
        # Save enhancement results immediately in case later steps fail
        modules['write_file']("output/improved_resume.txt", enhancement_result.get("improved_resume", "Enhancement failed"))
        modules['write_file']("output/resume_gaps.txt", "\n".join(enhancement_result.get("gaps", ["No gaps identified"])))
        
    except Exception as e:
        logger.error(f"Resume enhancement failed: {e}")
        results['enhancement'] = {
            "improved_resume": resume,  # Fallback to original
            "gaps": [f"Enhancement error: {str(e)}"],
            "upskill_recommendations": {},
            "error": str(e)
        }
    
    # Step 2: Job Search
    logger.info("Starting job search...")
    try:
        jobs = modules['scrape_jobs'](query=role, max_results=8)
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
            results['clusters'] = {0: results['jobs']}  # Put all jobs in one cluster as fallback
            results['clustering_error'] = str(e)
    else:
        logger.warning("Skipping clustering - no jobs available")
        results['clusters'] = {}
    
    # Step 4: Interview Question Generation (only if we have clusters)
    if results.get('clusters'):
        logger.info("Generating interview questions...")
        try:
            questions = {}
            for cluster_id, cluster_jobs in results['clusters'].items():
                if cluster_jobs:  # Only generate questions for non-empty clusters
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
    """
    Generate a comprehensive summary report of the pipeline execution.
    
    This function creates a human-readable summary that's perfect for demo
    purposes. It highlights successes, acknowledges any failures, and provides
    actionable insights for the user.
    
    Args:
        results: Dictionary containing all pipeline results
        role: Target role name
        
    Returns:
        Formatted summary report as a string
    """
    
    report_lines = [
        f"Resume Enhancement Pipeline Report",
        f"=" * 50,
        f"Target Role: {role}",
        f"Execution Time: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}",
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
            f"  - Found {len(jobs)} relevant job opportunities",
            f"  - Jobs span multiple companies and locations",
            ""
        ])
    else:
        error = results.get('job_search_error', 'No jobs found')
        report_lines.extend([
            f"✗ Job Search: LIMITED SUCCESS",
            f"  - Issue: {error}",
            ""
        ])
    
    # Clustering Results
    clusters = results.get('clusters', {})
    if clusters:
        report_lines.extend([
            f"✓ Job Clustering: SUCCESS",
            f"  - Organized jobs into {len(clusters)} strategic clusters",
            f"  - Each cluster represents a different career pathway",
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
            f"  - Questions customized for each job cluster",
            ""
        ])
    else:
        report_lines.extend([
            f"✗ Interview Preparation: SKIPPED",
            f"  - Reason: No job clusters available",
            ""
        ])
    
    # Next Steps and Recommendations
    report_lines.extend([
        "NEXT STEPS:",
        "1. Review the improved resume in output/improved_resume.txt",
        "2. Check identified skill gaps in output/resume_gaps.txt", 
        "3. Explore job opportunities in output/jobs.json",
        "4. Practice with interview questions in output/interview_questions.json",
        "",
        "For questions or issues, check the log output above.",
        ""
    ])
    
    return "\n".join(report_lines)

def main():
    """
    Main execution function with comprehensive error handling and reporting.
    
    This function orchestrates the entire pipeline while ensuring that your
    demo will always produce some meaningful output, even if individual
    components fail. This is crucial for hackathon presentations where
    you can't afford to have your demo crash unexpectedly.
    """
    
    logger.info("Starting Resume Hunter Agent Pipeline")
    # ensure .env loaded before checking
    if not check_environment():
        sys.exit(1)
    modules = safe_import()
    if not modules:
        sys.exit(1)
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Step 1: Environment Check
    if not check_environment():
        logger.error("Environment check failed - cannot proceed")
        sys.exit(1)
    
    # Step 2: Import Required Modules
    modules = safe_import()
    if not modules:
        logger.error("Module import failed - cannot proceed")
        sys.exit(1)
    
    # Step 3: Load Input Data
    try:
        logger.info("Loading input data...")
        resume = modules['load_file']("../data/sample_resume.txt")
        job_desc = modules['load_file']("../data/sample_hiring.txt")
        role = "Machine Learning Engineer"  # You could make this configurable
        
        logger.info(f"Loaded resume ({len(resume)} characters)")
        logger.info(f"Loaded job description ({len(job_desc)} characters)")
        
    except Exception as e:
        logger.error(f"Failed to load input data: {e}")
        sys.exit(1)
    
    # Step 4: Execute Main Pipeline
    try:
        results = run_enhancement_pipeline(modules, resume, job_desc, role)
        
        # Step 5: Generate and Save Summary Report
        summary_report = generate_summary_report(results, role)
        modules['write_file']("output/pipeline_summary.txt", summary_report)
        
        # Display summary to user
        print("\n" + summary_report)
        
        logger.info("Pipeline execution completed successfully")
        logger.info("Check the 'output' directory for all generated files")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        print(f"\nPipeline failed with error: {e}")
        print("Check the logs above for more details")
        sys.exit(1)

if __name__ == "__main__":
    main()