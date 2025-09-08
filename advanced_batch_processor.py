"""
Advanced Batch Processing System
- Enhanced analytics and reporting
- Automated workflows and scheduling
- Performance optimization
- File monitoring and auto-processing
- Comprehensive error handling
"""

import json
import os
import sys
import time
import threading
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd
from loguru import logger
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from unified_prescription_processor import UnifiedPrescriptionProcessor
from config.settings import Settings

class AdvancedBatchProcessor:
    """Advanced batch processing with analytics and automation"""
    
    def __init__(self):
        self.settings = Settings()
        self.processor = None
        
        # Processing queues and results
        self.processing_queue = []
        self.completed_results = []
        self.failed_results = []
        self.processing_stats = defaultdict(int)
        
        # Automation settings
        self.auto_processing_enabled = False
        self.monitoring_directories = []
        self.scheduled_jobs = []
        
        # Performance optimization
        self.max_concurrent_prescriptions = 3
        self.batch_size = 10
        self.performance_metrics = {
            "total_processed": 0,
            "avg_processing_time": 0.0,
            "success_rate": 0.0,
            "bottlenecks": [],
            "peak_hours": defaultdict(int)
        }
        
        # Analytics
        self.analytics_data = {
            "decision_trends": defaultdict(list),
            "error_patterns": defaultdict(int),
            "drug_analysis": defaultdict(int),
            "sut_compliance_trends": [],
            "processing_timeline": []
        }
        
        logger.info("Advanced Batch Processor initialized")
    
    # =========================================================================
    # CORE BATCH PROCESSING
    # =========================================================================
    
    async def process_batch_async(self, prescriptions: List[Dict], source: str = "batch") -> Dict[str, Any]:
        """Asynchronous batch processing with concurrent workers"""
        start_time = datetime.now()
        
        logger.info(f"Starting async batch processing: {len(prescriptions)} prescriptions")
        
        # Initialize processor if needed
        if not self.processor:
            self.processor = UnifiedPrescriptionProcessor()
        
        # Split into batches for optimal processing
        batches = self._create_optimal_batches(prescriptions)
        
        results = []
        total_processed = 0
        
        # Process batches with concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_prescriptions) as executor:
            futures = []
            
            for batch_idx, batch in enumerate(batches):
                logger.info(f"Submitting batch {batch_idx + 1}/{len(batches)} ({len(batch)} prescriptions)")
                
                future = executor.submit(self._process_batch_sync, batch, f"{source}_batch_{batch_idx}")
                futures.append(future)
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                    total_processed += len(batch_results)
                    
                    logger.info(f"Batch completed: {total_processed}/{len(prescriptions)} total processed")
                    
                except Exception as e:
                    logger.error(f"Batch processing failed: {e}")
        
        end_time = datetime.now()
        processing_duration = (end_time - start_time).total_seconds()
        
        # Generate comprehensive analytics
        analytics = self._generate_batch_analytics(results, processing_duration, source)
        
        # Update performance metrics
        self._update_performance_metrics(results, processing_duration)
        
        # Store results
        self.completed_results.extend(results)
        
        batch_summary = {
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "processing_duration_seconds": processing_duration,
                "source": source,
                "total_prescriptions": len(prescriptions),
                "successful_prescriptions": len(results),
                "failed_prescriptions": len(prescriptions) - len(results),
                "avg_processing_time": processing_duration / len(prescriptions) if prescriptions else 0
            },
            "results": results,
            "analytics": analytics,
            "performance": self.performance_metrics.copy()
        }
        
        logger.info(f"Async batch processing completed: {total_processed} prescriptions in {processing_duration:.2f}s")
        
        return batch_summary
    
    def _create_optimal_batches(self, prescriptions: List[Dict]) -> List[List[Dict]]:
        """Create optimally sized batches for processing"""
        
        # Dynamic batch sizing based on complexity
        batches = []
        current_batch = []
        current_complexity = 0
        
        for prescription in prescriptions:
            # Calculate prescription complexity
            complexity = self._calculate_prescription_complexity(prescription)
            
            # If adding this prescription would exceed batch limits, start new batch
            if (len(current_batch) >= self.batch_size or 
                current_complexity + complexity > self.batch_size * 2):
                
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_complexity = 0
            
            current_batch.append(prescription)
            current_complexity += complexity
        
        # Add final batch
        if current_batch:
            batches.append(current_batch)
        
        logger.info(f"Created {len(batches)} optimal batches from {len(prescriptions)} prescriptions")
        return batches
    
    def _calculate_prescription_complexity(self, prescription: Dict) -> int:
        """Calculate processing complexity score for a prescription"""
        
        complexity = 1  # Base complexity
        
        # More drugs = higher complexity
        drugs = prescription.get("drugs", [])
        complexity += len(drugs)
        
        # Report requirements add complexity
        if prescription.get("report_details") or prescription.get("rapor_no"):
            complexity += 2
        
        # Message codes add complexity
        if prescription.get("ilac_mesajlari"):
            complexity += 1
        
        # Patient age considerations (if available)
        if prescription.get("hasta_tc"):
            complexity += 1
        
        return min(complexity, 5)  # Cap at 5
    
    def _process_batch_sync(self, batch: List[Dict], source: str) -> List[Dict]:
        """Synchronous processing of a single batch"""
        
        batch_results = []
        
        for prescription in batch:
            try:
                result = self.processor.process_single_prescription(prescription, source)
                batch_results.append(result)
                
                # Small delay for rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to process prescription {prescription.get('recete_no', 'N/A')}: {e}")
                
                # Create error result
                error_result = {
                    "prescription_id": prescription.get("recete_no", "UNKNOWN"),
                    "final_decision": "error",
                    "error": str(e),
                    "processing_metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "source": source,
                        "error_type": type(e).__name__
                    }
                }
                
                batch_results.append(error_result)
                self.failed_results.append(error_result)
        
        return batch_results
    
    # =========================================================================
    # ENHANCED ANALYTICS
    # =========================================================================
    
    def _generate_batch_analytics(self, results: List[Dict], duration: float, source: str) -> Dict[str, Any]:
        """Generate comprehensive analytics for batch results"""
        
        if not results:
            return {"error": "No results to analyze"}
        
        analytics = {
            "summary": self._generate_summary_analytics(results, duration),
            "decision_analysis": self._analyze_decisions(results),
            "sut_compliance_analysis": self._analyze_sut_compliance(results),
            "performance_analysis": self._analyze_performance(results, duration),
            "error_analysis": self._analyze_errors(results),
            "drug_analysis": self._analyze_drugs(results),
            "temporal_analysis": self._analyze_temporal_patterns(results),
            "recommendations": self._generate_recommendations(results)
        }
        
        # Update historical analytics
        self._update_historical_analytics(analytics, source)
        
        return analytics
    
    def _generate_summary_analytics(self, results: List[Dict], duration: float) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        total = len(results)
        
        decisions = [r.get("final_decision", "unknown") for r in results]
        decision_counts = Counter(decisions)
        
        # Processing times
        processing_times = []
        for result in results:
            pt = result.get("processing_metadata", {}).get("processing_time_seconds", 0)
            if pt > 0:
                processing_times.append(pt)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Claude API usage
        claude_used_count = sum(1 for r in results if r.get("ai_analysis", {}).get("claude_used", False))
        claude_usage_rate = (claude_used_count / total * 100) if total > 0 else 0
        
        # Confidence scores
        confidence_scores = []
        for result in results:
            ai_conf = result.get("ai_analysis", {}).get("confidence", 0)
            sut_conf = result.get("sut_analysis", {}).get("confidence", 0)
            if ai_conf > 0 or sut_conf > 0:
                confidence_scores.append(max(ai_conf, sut_conf))
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "total_prescriptions": total,
            "batch_duration_seconds": duration,
            "avg_processing_time_seconds": avg_processing_time,
            "decisions": dict(decision_counts),
            "success_rate": ((total - decision_counts.get("error", 0)) / total * 100) if total > 0 else 0,
            "claude_usage_rate": claude_usage_rate,
            "average_confidence": avg_confidence,
            "throughput_per_minute": (total / (duration / 60)) if duration > 0 else 0
        }
    
    def _analyze_decisions(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze decision patterns"""
        
        decisions = []
        
        for result in results:
            final_decision = result.get("final_decision", "unknown")
            sut_decision = result.get("sut_analysis", {}).get("action", "unknown")
            ai_decision = result.get("ai_analysis", {}).get("action", "unknown")
            
            decisions.append({
                "final": final_decision,
                "sut": sut_decision,
                "ai": ai_decision,
                "prescription_id": result.get("prescription_id", "N/A")
            })
        
        # Decision agreement analysis
        agreements = {"perfect": 0, "partial": 0, "conflict": 0}
        
        for decision in decisions:
            if decision["sut"] == decision["ai"] == decision["final"]:
                agreements["perfect"] += 1
            elif decision["sut"] == decision["ai"] or decision["final"] in [decision["sut"], decision["ai"]]:
                agreements["partial"] += 1
            else:
                agreements["conflict"] += 1
        
        # Most common decision patterns
        decision_patterns = Counter(f"{d['sut']}->{d['ai']}->{d['final']}" for d in decisions)
        
        return {
            "decision_distribution": Counter(d["final"] for d in decisions),
            "sut_vs_ai_agreement": agreements,
            "common_patterns": dict(decision_patterns.most_common(5)),
            "conflict_cases": [d["prescription_id"] for d in decisions 
                             if d["sut"] != d["ai"] and d["final"] not in [d["sut"], d["ai"]]]
        }
    
    def _analyze_sut_compliance(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze SUT compliance patterns"""
        
        compliance_data = []
        
        for result in results:
            sut_analysis = result.get("sut_analysis", {})
            
            compliance_data.append({
                "compliant": sut_analysis.get("compliant", False),
                "issues_count": sut_analysis.get("issues_count", 0),
                "warnings_count": sut_analysis.get("warnings_count", 0),
                "confidence": sut_analysis.get("confidence", 0),
                "prescription_id": result.get("prescription_id", "N/A")
            })
        
        compliant_count = sum(1 for d in compliance_data if d["compliant"])
        total_issues = sum(d["issues_count"] for d in compliance_data)
        total_warnings = sum(d["warnings_count"] for d in compliance_data)
        
        # Issue severity distribution
        high_severity = sum(1 for d in compliance_data if d["issues_count"] >= 3)
        medium_severity = sum(1 for d in compliance_data if 1 <= d["issues_count"] < 3)
        low_severity = sum(1 for d in compliance_data if d["issues_count"] == 0 and d["warnings_count"] > 0)
        
        return {
            "compliance_rate": (compliant_count / len(compliance_data) * 100) if compliance_data else 0,
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "severity_distribution": {
                "high": high_severity,
                "medium": medium_severity, 
                "low": low_severity,
                "none": len(compliance_data) - high_severity - medium_severity - low_severity
            },
            "avg_issues_per_prescription": total_issues / len(compliance_data) if compliance_data else 0,
            "most_problematic_prescriptions": [d["prescription_id"] for d in compliance_data 
                                             if d["issues_count"] >= 3]
        }
    
    def _analyze_performance(self, results: List[Dict], batch_duration: float) -> Dict[str, Any]:
        """Analyze processing performance"""
        
        processing_times = []
        sut_times = []
        ai_times = []
        
        for result in results:
            metadata = result.get("processing_metadata", {})
            pt = metadata.get("processing_time_seconds", 0)
            
            if pt > 0:
                processing_times.append(pt)
            
            # Extract SUT and AI processing times if available
            sut_time = metadata.get("sut_processing_time", 0)
            ai_time = metadata.get("ai_processing_time", 0)
            
            if sut_time > 0:
                sut_times.append(sut_time)
            if ai_time > 0:
                ai_times.append(ai_time)
        
        # Performance statistics
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
            
            # Identify bottlenecks
            slow_prescriptions = [i for i, t in enumerate(processing_times) if t > avg_time * 2]
        else:
            avg_time = min_time = max_time = 0
            slow_prescriptions = []
        
        return {
            "batch_duration": batch_duration,
            "total_prescriptions": len(results),
            "avg_processing_time": avg_time,
            "min_processing_time": min_time,
            "max_processing_time": max_time,
            "throughput_per_second": len(results) / batch_duration if batch_duration > 0 else 0,
            "slow_prescriptions_count": len(slow_prescriptions),
            "avg_sut_time": sum(sut_times) / len(sut_times) if sut_times else 0,
            "avg_ai_time": sum(ai_times) / len(ai_times) if ai_times else 0,
            "bottlenecks": self._identify_bottlenecks(results)
        }
    
    def _identify_bottlenecks(self, results: List[Dict]) -> List[str]:
        """Identify performance bottlenecks"""
        
        bottlenecks = []
        
        # Check AI processing times
        ai_times = [r.get("processing_metadata", {}).get("ai_processing_time", 0) for r in results]
        avg_ai_time = sum(ai_times) / len(ai_times) if ai_times else 0
        
        if avg_ai_time > 3.0:
            bottlenecks.append("High AI processing time - consider model optimization")
        
        # Check SUT processing
        sut_times = [r.get("processing_metadata", {}).get("sut_processing_time", 0) for r in results]
        avg_sut_time = sum(sut_times) / len(sut_times) if sut_times else 0
        
        if avg_sut_time > 1.0:
            bottlenecks.append("High SUT processing time - database optimization needed")
        
        # Check error rates
        error_rate = sum(1 for r in results if r.get("final_decision") == "error") / len(results) * 100
        if error_rate > 10:
            bottlenecks.append(f"High error rate ({error_rate:.1f}%) - review error handling")
        
        # Check Claude API usage
        claude_used = sum(1 for r in results if r.get("ai_analysis", {}).get("claude_used", False))
        if claude_used / len(results) < 0.5:
            bottlenecks.append("Low Claude API usage - check API connectivity")
        
        return bottlenecks
    
    def _analyze_errors(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns"""
        
        errors = []
        error_types = Counter()
        
        for result in results:
            if result.get("final_decision") == "error" or "error" in result:
                error_info = {
                    "prescription_id": result.get("prescription_id", "N/A"),
                    "error": result.get("error", "Unknown error"),
                    "error_type": result.get("processing_metadata", {}).get("error_type", "Unknown")
                }
                errors.append(error_info)
                error_types[error_info["error_type"]] += 1
        
        # Common error patterns
        error_messages = [e["error"] for e in errors]
        common_errors = Counter(error_messages).most_common(5)
        
        return {
            "total_errors": len(errors),
            "error_rate": (len(errors) / len(results) * 100) if results else 0,
            "error_types": dict(error_types),
            "common_errors": dict(common_errors),
            "failed_prescriptions": [e["prescription_id"] for e in errors]
        }
    
    def _analyze_drugs(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze drug-related patterns"""
        
        all_drugs = []
        drug_decisions = defaultdict(list)
        
        for result in results:
            # Extract drugs from raw data if available
            raw_data = result.get("raw_data", {}).get("prescription_data", {})
            drugs = raw_data.get("drugs", [])
            
            decision = result.get("final_decision", "unknown")
            
            for drug in drugs:
                drug_name = drug.get("ilac_adi", "Unknown").upper()
                all_drugs.append(drug_name)
                drug_decisions[drug_name].append(decision)
        
        # Drug frequency analysis
        drug_frequency = Counter(all_drugs)
        
        # Drug decision patterns
        drug_approval_rates = {}
        for drug, decisions in drug_decisions.items():
            if decisions:
                approval_rate = (decisions.count("approve") / len(decisions)) * 100
                drug_approval_rates[drug] = approval_rate
        
        return {
            "total_unique_drugs": len(drug_frequency),
            "most_common_drugs": dict(drug_frequency.most_common(10)),
            "drug_approval_rates": dict(sorted(drug_approval_rates.items(), 
                                             key=lambda x: x[1], reverse=True)[:10]),
            "problematic_drugs": [drug for drug, rate in drug_approval_rates.items() if rate < 50]
        }
    
    def _analyze_temporal_patterns(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal processing patterns"""
        
        timestamps = []
        
        for result in results:
            timestamp_str = result.get("processing_metadata", {}).get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamps.append(timestamp)
                except:
                    continue
        
        if not timestamps:
            return {"error": "No valid timestamps found"}
        
        # Hour distribution
        hours = [ts.hour for ts in timestamps]
        hour_distribution = Counter(hours)
        
        # Processing time trends
        processing_times = []
        for i, result in enumerate(results):
            pt = result.get("processing_metadata", {}).get("processing_time_seconds", 0)
            if pt > 0 and i < len(timestamps):
                processing_times.append((timestamps[i], pt))
        
        return {
            "processing_hour_distribution": dict(hour_distribution),
            "peak_processing_hour": max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None,
            "avg_processing_time_by_hour": self._calculate_hourly_averages(processing_times),
            "processing_duration": {
                "start": min(timestamps).isoformat() if timestamps else None,
                "end": max(timestamps).isoformat() if timestamps else None,
                "total_minutes": ((max(timestamps) - min(timestamps)).total_seconds() / 60) if len(timestamps) > 1 else 0
            }
        }
    
    def _calculate_hourly_averages(self, processing_times: List[tuple]) -> Dict[int, float]:
        """Calculate average processing times by hour"""
        
        hourly_times = defaultdict(list)
        
        for timestamp, processing_time in processing_times:
            hourly_times[timestamp.hour].append(processing_time)
        
        return {hour: sum(times) / len(times) for hour, times in hourly_times.items()}
    
    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        if not results:
            return ["No results available for analysis"]
        
        # Performance recommendations
        avg_time = sum(r.get("processing_metadata", {}).get("processing_time_seconds", 0) 
                      for r in results) / len(results)
        
        if avg_time > 5.0:
            recommendations.append("Consider increasing batch size or parallel processing to improve throughput")
        
        # Error rate recommendations
        error_rate = sum(1 for r in results if r.get("final_decision") == "error") / len(results) * 100
        
        if error_rate > 15:
            recommendations.append("High error rate detected - review input data quality and error handling")
        elif error_rate > 5:
            recommendations.append("Moderate error rate - consider implementing retry logic for failed prescriptions")
        
        # Decision pattern recommendations
        hold_rate = sum(1 for r in results if r.get("final_decision") == "hold") / len(results) * 100
        
        if hold_rate > 50:
            recommendations.append("High hold rate suggests SUT rules may be too strict - review and adjust thresholds")
        
        # Claude API recommendations
        claude_usage = sum(1 for r in results if r.get("ai_analysis", {}).get("claude_used", False)) / len(results) * 100
        
        if claude_usage < 30:
            recommendations.append("Low Claude API usage - check API connectivity and configuration")
        
        # SUT compliance recommendations
        sut_issues = sum(r.get("sut_analysis", {}).get("issues_count", 0) for r in results)
        if sut_issues / len(results) > 2:
            recommendations.append("High SUT non-compliance - consider updating SUT rules database")
        
        return recommendations
    
    def _update_historical_analytics(self, analytics: Dict, source: str):
        """Update historical analytics data"""
        
        timestamp = datetime.now()
        
        # Update decision trends
        decisions = analytics.get("decision_analysis", {}).get("decision_distribution", {})
        for decision, count in decisions.items():
            self.analytics_data["decision_trends"][decision].append({
                "timestamp": timestamp.isoformat(),
                "count": count,
                "source": source
            })
        
        # Update SUT compliance trends
        sut_analysis = analytics.get("sut_compliance_analysis", {})
        self.analytics_data["sut_compliance_trends"].append({
            "timestamp": timestamp.isoformat(),
            "compliance_rate": sut_analysis.get("compliance_rate", 0),
            "total_issues": sut_analysis.get("total_issues", 0),
            "source": source
        })
        
        # Update processing timeline
        summary = analytics.get("summary", {})
        self.analytics_data["processing_timeline"].append({
            "timestamp": timestamp.isoformat(),
            "total_prescriptions": summary.get("total_prescriptions", 0),
            "avg_processing_time": summary.get("avg_processing_time_seconds", 0),
            "success_rate": summary.get("success_rate", 0),
            "source": source
        })
    
    def _update_performance_metrics(self, results: List[Dict], duration: float):
        """Update global performance metrics"""
        
        total_processed = len(results)
        self.performance_metrics["total_processed"] += total_processed
        
        # Update average processing time
        if results:
            current_avg = self.performance_metrics["avg_processing_time"]
            new_avg = duration / total_processed
            
            # Weighted average
            total_batches = len(self.analytics_data["processing_timeline"])
            if total_batches > 0:
                self.performance_metrics["avg_processing_time"] = (
                    (current_avg * (total_batches - 1) + new_avg) / total_batches
                )
            else:
                self.performance_metrics["avg_processing_time"] = new_avg
        
        # Update success rate
        successful = sum(1 for r in results if r.get("final_decision") != "error")
        if total_processed > 0:
            batch_success_rate = (successful / total_processed) * 100
            
            # Update global success rate
            total_processed_global = self.performance_metrics["total_processed"]
            if total_processed_global > total_processed:
                current_success_rate = self.performance_metrics["success_rate"]
                self.performance_metrics["success_rate"] = (
                    (current_success_rate * (total_processed_global - total_processed) + 
                     batch_success_rate * total_processed) / total_processed_global
                )
            else:
                self.performance_metrics["success_rate"] = batch_success_rate
        
        # Update peak hours
        current_hour = datetime.now().hour
        self.performance_metrics["peak_hours"][current_hour] += total_processed
    
    # =========================================================================
    # AUTOMATED WORKFLOWS
    # =========================================================================
    
    def setup_file_monitoring(self, directories: List[str], patterns: List[str] = None):
        """Setup automated file monitoring for new prescriptions"""
        
        if patterns is None:
            patterns = ["*.json"]
        
        self.monitoring_directories = directories
        
        logger.info(f"File monitoring setup for directories: {directories}")
        logger.info(f"Monitoring patterns: {patterns}")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._file_monitor_worker, args=(directories, patterns))
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _file_monitor_worker(self, directories: List[str], patterns: List[str]):
        """Worker thread for file monitoring"""
        
        processed_files = set()
        
        logger.info("File monitor started")
        
        while self.auto_processing_enabled:
            for directory in directories:
                if not os.path.exists(directory):
                    continue
                    
                for pattern in patterns:
                    import glob
                    files = glob.glob(os.path.join(directory, pattern))
                    
                    for file_path in files:
                        if file_path not in processed_files:
                            logger.info(f"New file detected: {file_path}")
                            
                            try:
                                # Process the file
                                self._process_file_automatically(file_path)
                                processed_files.add(file_path)
                                
                            except Exception as e:
                                logger.error(f"Auto-processing failed for {file_path}: {e}")
            
            time.sleep(10)  # Check every 10 seconds
    
    def _process_file_automatically(self, file_path: str):
        """Automatically process a detected file"""
        
        try:
            # Load and validate file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.warning(f"File {file_path} is not a prescription list, skipping")
                return
            
            # Process asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.process_batch_async(data, f"auto_{Path(file_path).stem}")
            )
            
            # Save results
            output_file = file_path.replace(".json", f"_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Auto-processing completed: {file_path} -> {output_file}")
            
        except Exception as e:
            logger.error(f"Auto-processing error for {file_path}: {e}")
    
    def schedule_batch_processing(self, schedule_time: str, source_directory: str, 
                                pattern: str = "*.json", recurring: bool = True):
        """Schedule regular batch processing"""
        
        def scheduled_job():
            logger.info(f"Running scheduled batch processing: {source_directory}")
            
            try:
                # Find files to process
                import glob
                files = glob.glob(os.path.join(source_directory, pattern))
                
                if not files:
                    logger.info("No files found for scheduled processing")
                    return
                
                # Process all files
                all_prescriptions = []
                
                for file_path in files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        if isinstance(data, list):
                            all_prescriptions.extend(data)
                            
                    except Exception as e:
                        logger.error(f"Failed to load {file_path}: {e}")
                
                if all_prescriptions:
                    # Run async processing
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        self.process_batch_async(all_prescriptions, "scheduled")
                    )
                    
                    # Save results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = os.path.join(source_directory, f"scheduled_results_{timestamp}.json")
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"Scheduled processing completed: {len(all_prescriptions)} prescriptions")
                
            except Exception as e:
                logger.error(f"Scheduled processing failed: {e}")
        
        # Schedule the job
        if recurring:
            schedule.every().day.at(schedule_time).do(scheduled_job)
        else:
            # One-time job
            target_time = datetime.strptime(schedule_time, "%H:%M").time()
            now = datetime.now().time()
            
            if target_time > now:
                # Schedule for today
                schedule.every().day.at(schedule_time).do(scheduled_job).tag("one-time")
            else:
                # Schedule for tomorrow
                schedule.every().day.at(schedule_time).do(scheduled_job).tag("one-time")
        
        # Start scheduler thread if not already running
        if not hasattr(self, '_scheduler_thread') or not self._scheduler_thread.is_alive():
            self._scheduler_thread = threading.Thread(target=self._scheduler_worker)
            self._scheduler_thread.daemon = True
            self._scheduler_thread.start()
        
        logger.info(f"Batch processing scheduled for {schedule_time} ({'recurring' if recurring else 'one-time'})")
    
    def _scheduler_worker(self):
        """Worker thread for scheduled jobs"""
        
        logger.info("Scheduler worker started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # =========================================================================
    # REPORTING AND EXPORT
    # =========================================================================
    
    def generate_comprehensive_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive processing report"""
        
        if output_file is None:
            output_file = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive_batch_analysis",
                "version": "1.0.0"
            },
            "summary": {
                "total_prescriptions_processed": self.performance_metrics["total_processed"],
                "total_batches_completed": len(self.analytics_data["processing_timeline"]),
                "overall_success_rate": self.performance_metrics["success_rate"],
                "average_processing_time": self.performance_metrics["avg_processing_time"],
                "peak_processing_hours": dict(self.performance_metrics["peak_hours"])
            },
            "analytics": {
                "decision_trends": dict(self.analytics_data["decision_trends"]),
                "sut_compliance_trends": self.analytics_data["sut_compliance_trends"],
                "processing_timeline": self.analytics_data["processing_timeline"],
                "error_patterns": dict(self.analytics_data["error_patterns"]),
                "drug_analysis": dict(self.analytics_data["drug_analysis"])
            },
            "performance": self.performance_metrics,
            "recent_results": self.completed_results[-10:] if self.completed_results else [],
            "failed_results": self.failed_results[-10:] if self.failed_results else []
        }
        
        # Save report
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Comprehensive report generated: {output_file}")
        
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report
    
    def export_to_excel(self, output_file: Optional[str] = None) -> bool:
        """Export analytics to Excel format"""
        
        try:
            if output_file is None:
                output_file = f"batch_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Summary sheet
                if self.analytics_data["processing_timeline"]:
                    summary_df = pd.DataFrame(self.analytics_data["processing_timeline"])
                    summary_df.to_excel(writer, sheet_name="Processing Summary", index=False)
                
                # SUT Compliance sheet
                if self.analytics_data["sut_compliance_trends"]:
                    sut_df = pd.DataFrame(self.analytics_data["sut_compliance_trends"])
                    sut_df.to_excel(writer, sheet_name="SUT Compliance", index=False)
                
                # Performance metrics
                perf_data = []
                for key, value in self.performance_metrics.items():
                    if key != "peak_hours":  # Skip complex nested data
                        perf_data.append({"metric": key, "value": value})
                
                if perf_data:
                    perf_df = pd.DataFrame(perf_data)
                    perf_df.to_excel(writer, sheet_name="Performance", index=False)
                
                # Recent results
                if self.completed_results:
                    results_data = []
                    for result in self.completed_results[-100:]:  # Last 100 results
                        results_data.append({
                            "prescription_id": result.get("prescription_id", "N/A"),
                            "final_decision": result.get("final_decision", "unknown"),
                            "sut_action": result.get("sut_analysis", {}).get("action", "N/A"),
                            "ai_action": result.get("ai_analysis", {}).get("action", "N/A"),
                            "processing_time": result.get("processing_metadata", {}).get("processing_time_seconds", 0),
                            "timestamp": result.get("processing_metadata", {}).get("timestamp", "")
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    results_df.to_excel(writer, sheet_name="Recent Results", index=False)
            
            logger.info(f"Analytics exported to Excel: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return False
    
    # =========================================================================
    # CONTROL METHODS
    # =========================================================================
    
    def start_automation(self, monitor_dirs: List[str] = None):
        """Start automated processing"""
        
        self.auto_processing_enabled = True
        
        if monitor_dirs:
            self.setup_file_monitoring(monitor_dirs)
        
        logger.info("Advanced batch processor automation started")
    
    def stop_automation(self):
        """Stop automated processing"""
        
        self.auto_processing_enabled = False
        logger.info("Advanced batch processor automation stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current processor status"""
        
        return {
            "automation_enabled": self.auto_processing_enabled,
            "monitoring_directories": self.monitoring_directories,
            "scheduled_jobs": len(schedule.jobs),
            "completed_results": len(self.completed_results),
            "failed_results": len(self.failed_results),
            "performance_metrics": self.performance_metrics,
            "queue_size": len(self.processing_queue)
        }
    
    def clear_results(self):
        """Clear all results and reset analytics"""
        
        self.completed_results.clear()
        self.failed_results.clear()
        self.processing_queue.clear()
        self.analytics_data = {
            "decision_trends": defaultdict(list),
            "error_patterns": defaultdict(int),
            "drug_analysis": defaultdict(int),
            "sut_compliance_trends": [],
            "processing_timeline": []
        }
        
        logger.info("Results and analytics cleared")

# =========================================================================
# TEST AND DEMO FUNCTIONS
# =========================================================================

async def test_advanced_batch_processing():
    """Test advanced batch processing features"""
    
    print("=== ADVANCED BATCH PROCESSOR TEST ===")
    
    processor = AdvancedBatchProcessor()
    
    # Test data
    if os.path.exists("manual_detailed_prescriptions.json"):
        with open("manual_detailed_prescriptions.json", 'r', encoding='utf-8') as f:
            test_prescriptions = json.load(f)
        
        print(f"Testing with {len(test_prescriptions)} prescriptions...")
        
        # Run advanced batch processing
        result = await processor.process_batch_async(test_prescriptions, "test")
        
        print("\\n=== BATCH PROCESSING RESULTS ===")
        metadata = result["metadata"]
        print(f"Duration: {metadata['processing_duration_seconds']:.2f}s")
        print(f"Throughput: {metadata['total_prescriptions'] / metadata['processing_duration_seconds']:.2f} prescriptions/sec")
        print(f"Success Rate: {((metadata['successful_prescriptions'] / metadata['total_prescriptions']) * 100):.1f}%")
        
        # Show analytics
        analytics = result["analytics"]
        print("\\n=== ANALYTICS SUMMARY ===")
        print(f"Decision Distribution: {analytics['decision_analysis']['decision_distribution']}")
        print(f"SUT Compliance Rate: {analytics['sut_compliance_analysis']['compliance_rate']:.1f}%")
        print(f"Performance Bottlenecks: {analytics['performance_analysis']['bottlenecks']}")
        
        # Generate reports
        print("\\n=== GENERATING REPORTS ===")
        processor.generate_comprehensive_report("test_comprehensive_report.json")
        
        if processor.export_to_excel("test_analytics.xlsx"):
            print("Excel report generated successfully")
        
        print("\\n=== RECOMMENDATIONS ===")
        for rec in analytics["recommendations"]:
            print(f"• {rec}")
        
        return True
    
    else:
        print("Test file not found: manual_detailed_prescriptions.json")
        return False

def main():
    """Main test function"""
    
    print("[*] Advanced Batch Processor - Testing Suite")
    print("=" * 60)
    
    # Run async test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    success = loop.run_until_complete(test_advanced_batch_processing())
    
    if success:
        print("\\n[*] All tests completed successfully!")
    else:
        print("\\n[!] Some tests failed - check logs")

if __name__ == "__main__":
    main()