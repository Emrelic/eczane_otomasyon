"""
Full GUI for Unified Prescription Processor
CustomTkinter ile modern arayüz - tüm özellikler dahil
- Medula login interface
- Real-time processing
- Results visualization
- Settings management
- Live status updates
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import threading
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from unified_prescription_processor import UnifiedPrescriptionProcessor
from config.settings import Settings

# CustomTkinter theme
ctk.set_appearance_mode("system")  # "system", "dark", "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class UnifiedProcessorGUI:
    """Full featured GUI for prescription processing"""
    
    def __init__(self):
        # Main window
        self.root = ctk.CTk()
        self.root.title("Eczane Otomasyon - Unified Processor v2.0")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize processor
        self.processor = None
        self.processing_thread = None
        self.is_processing = False
        
        # Results storage
        self.current_results = []
        self.processing_stats = {}
        
        # GUI setup
        self.setup_gui()
        self.setup_status_bar()
        
        # Load settings
        self.load_settings()
        
        print("[*] Unified Processor GUI initialized")
    
    def setup_gui(self):
        """Main GUI setup"""
        
        # ===== MAIN CONTAINER =====
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ===== HEADER =====
        self.setup_header()
        
        # ===== MAIN CONTENT - TABVIEW =====
        self.setup_tabview()
        
    def setup_header(self):
        """Header section"""
        header_frame = ctk.CTkFrame(self.main_container, height=80)
        header_frame.pack(fill="x", padx=5, pady=(5, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="ECZANE OTOMASYON - UNIFIED PROCESSOR",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(header_frame, width=200, height=60)
        self.status_frame.pack(side="right", padx=20, pady=10)
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="[*] READY", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.status_label.pack(pady=20)
        
    def setup_tabview(self):
        """Main tabview setup"""
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tabs
        self.tab_json = self.tabview.add("[FILE] JSON Processing")
        self.tab_medula = self.tabview.add("[NET] Live Medula")
        self.tab_results = self.tabview.add("[STATS] Results")
        self.tab_settings = self.tabview.add("[SET] Settings")
        self.tab_logs = self.tabview.add("[LOG] Logs")
        
        # Setup each tab
        self.setup_json_tab()
        self.setup_medula_tab()
        self.setup_results_tab()
        self.setup_settings_tab()
        self.setup_logs_tab()
        
    # =========================================================================
    # JSON PROCESSING TAB
    # =========================================================================
    
    def setup_json_tab(self):
        """JSON processing tab"""
        
        # File selection frame
        file_frame = ctk.CTkFrame(self.tab_json, height=120)
        file_frame.pack(fill="x", padx=10, pady=10)
        file_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            file_frame, 
            text="[FILE] JSON File Processing",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # File selection
        file_select_frame = ctk.CTkFrame(file_frame)
        file_select_frame.pack(fill="x", padx=20, pady=5)
        
        self.json_file_var = tk.StringVar(value="No file selected")
        self.json_file_label = ctk.CTkLabel(
            file_select_frame, 
            textvariable=self.json_file_var,
            font=ctk.CTkFont(size=12)
        )
        self.json_file_label.pack(side="left", padx=10, pady=10)
        
        self.select_file_btn = ctk.CTkButton(
            file_select_frame,
            text="[OPEN] Select JSON File",
            command=self.select_json_file,
            width=150
        )
        self.select_file_btn.pack(side="right", padx=10, pady=10)
        
        # Processing controls
        control_frame = ctk.CTkFrame(self.tab_json, height=100)
        control_frame.pack(fill="x", padx=10, pady=5)
        control_frame.pack_propagate(False)
        
        # Start button
        self.process_json_btn = ctk.CTkButton(
            control_frame,
            text="[*] Start JSON Processing",
            command=self.start_json_processing,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            state="disabled"
        )
        self.process_json_btn.pack(pady=30)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(self.tab_json, height=100)
        progress_frame.pack(fill="x", padx=10, pady=5)
        progress_frame.pack_propagate(False)
        
        self.json_progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to process...",
            font=ctk.CTkFont(size=14)
        )
        self.json_progress_label.pack(pady=10)
        
        self.json_progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.json_progress_bar.pack(pady=10)
        self.json_progress_bar.set(0)
        
        # Quick stats frame
        stats_frame = ctk.CTkFrame(self.tab_json)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            stats_frame,
            text="📈 Processing Statistics",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.json_stats_text = ctk.CTkTextbox(stats_frame, height=200)
        self.json_stats_text.pack(fill="both", expand=True, padx=20, pady=10)
        self.json_stats_text.insert("1.0", "No processing completed yet...")
        
    # =========================================================================
    # MEDULA LIVE TAB
    # =========================================================================
    
    def setup_medula_tab(self):
        """Live Medula processing tab"""
        
        # Connection frame
        conn_frame = ctk.CTkFrame(self.tab_medula, height=200)
        conn_frame.pack(fill="x", padx=10, pady=10)
        conn_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            conn_frame,
            text="[NET] Live Medula Connection",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Login info frame
        login_info_frame = ctk.CTkFrame(conn_frame)
        login_info_frame.pack(fill="x", padx=20, pady=10)
        
        # Username
        ctk.CTkLabel(login_info_frame, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.medula_username_var = tk.StringVar()
        self.medula_username_entry = ctk.CTkEntry(
            login_info_frame, 
            textvariable=self.medula_username_var,
            width=200
        )
        self.medula_username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Password
        ctk.CTkLabel(login_info_frame, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.medula_password_var = tk.StringVar()
        self.medula_password_entry = ctk.CTkEntry(
            login_info_frame, 
            textvariable=self.medula_password_var,
            show="*",
            width=200
        )
        self.medula_password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Group selection
        ctk.CTkLabel(login_info_frame, text="Group:").grid(row=0, column=2, padx=20, pady=5, sticky="w")
        self.medula_group_var = tk.StringVar(value="A")
        self.medula_group_combo = ctk.CTkComboBox(
            login_info_frame,
            values=["A", "B", "C"],
            variable=self.medula_group_var,
            width=100
        )
        self.medula_group_combo.grid(row=0, column=3, padx=10, pady=5)
        
        # Limit
        ctk.CTkLabel(login_info_frame, text="Limit:").grid(row=1, column=2, padx=20, pady=5, sticky="w")
        self.medula_limit_var = tk.StringVar(value="5")
        self.medula_limit_entry = ctk.CTkEntry(
            login_info_frame,
            textvariable=self.medula_limit_var,
            width=100
        )
        self.medula_limit_entry.grid(row=1, column=3, padx=10, pady=5)
        
        # Connection button
        self.medula_connect_btn = ctk.CTkButton(
            conn_frame,
            text="[LINK] Connect & Process",
            command=self.start_medula_processing,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        self.medula_connect_btn.pack(pady=20)
        
        # Status frame
        medula_status_frame = ctk.CTkFrame(self.tab_medula)
        medula_status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            medula_status_frame,
            text="[STATS] Live Processing Status",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.medula_status_text = ctk.CTkTextbox(medula_status_frame)
        self.medula_status_text.pack(fill="both", expand=True, padx=20, pady=10)
        self.medula_status_text.insert("1.0", "Ready to connect to Medula...\n\n⚠️ Note: CAPTCHA solving will require manual intervention")
        
    # =========================================================================
    # RESULTS TAB
    # =========================================================================
    
    def setup_results_tab(self):
        """Results visualization tab"""
        
        # Controls frame
        results_controls = ctk.CTkFrame(self.tab_results, height=80)
        results_controls.pack(fill="x", padx=10, pady=10)
        results_controls.pack_propagate(False)
        
        # Export button
        self.export_btn = ctk.CTkButton(
            results_controls,
            text="[SAVE] Export Results",
            command=self.export_results,
            state="disabled"
        )
        self.export_btn.pack(side="left", padx=20, pady=20)
        
        # Clear button
        self.clear_results_btn = ctk.CTkButton(
            results_controls,
            text="[DEL] Clear Results",
            command=self.clear_results
        )
        self.clear_results_btn.pack(side="left", padx=10, pady=20)
        
        # Results summary
        self.results_summary_label = ctk.CTkLabel(
            results_controls,
            text="No results available",
            font=ctk.CTkFont(size=14)
        )
        self.results_summary_label.pack(side="right", padx=20, pady=20)
        
        # Results table frame
        table_frame = ctk.CTkFrame(self.tab_results)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Table
        self.setup_results_table(table_frame)
        
    def setup_results_table(self, parent):
        """Setup results table"""
        
        # Table with scrollbar
        table_container = ctk.CTkFrame(parent)
        table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Treeview for results
        columns = ("ID", "Patient", "Decision", "SUT", "AI", "Processing Time", "Timestamp")
        
        self.results_tree = ttk.Treeview(
            table_container, 
            columns=columns,
            show="headings",
            height=15
        )
        
        # Column headings
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == "ID":
                self.results_tree.column(col, width=100)
            elif col == "Patient":
                self.results_tree.column(col, width=150)
            elif col == "Decision":
                self.results_tree.column(col, width=80)
            elif col in ["SUT", "AI"]:
                self.results_tree.column(col, width=60)
            elif col == "Processing Time":
                self.results_tree.column(col, width=100)
            else:
                self.results_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.results_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
    # =========================================================================
    # SETTINGS TAB  
    # =========================================================================
    
    def setup_settings_tab(self):
        """Settings management tab"""
        
        # Settings sections
        self.setup_api_settings()
        self.setup_processing_settings()
        self.setup_system_settings()
        
    def setup_api_settings(self):
        """API settings section"""
        
        api_frame = ctk.CTkFrame(self.tab_settings, height=200)
        api_frame.pack(fill="x", padx=10, pady=10)
        api_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            api_frame,
            text="[KEY] API Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        api_grid = ctk.CTkFrame(api_frame)
        api_grid.pack(fill="x", padx=20, pady=10)
        
        # Claude API Key
        ctk.CTkLabel(api_grid, text="Claude API Key:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.claude_api_var = tk.StringVar()
        self.claude_api_entry = ctk.CTkEntry(
            api_grid,
            textvariable=self.claude_api_var,
            show="*",
            width=400
        )
        self.claude_api_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # AI Provider
        ctk.CTkLabel(api_grid, text="AI Provider:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ai_provider_var = tk.StringVar(value="claude")
        self.ai_provider_combo = ctk.CTkComboBox(
            api_grid,
            values=["claude", "openai"],
            variable=self.ai_provider_var,
            width=150
        )
        self.ai_provider_combo.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
    def setup_processing_settings(self):
        """Processing settings section"""
        
        proc_frame = ctk.CTkFrame(self.tab_settings, height=150)
        proc_frame.pack(fill="x", padx=10, pady=5)
        proc_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            proc_frame,
            text="[SET] Processing Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        proc_grid = ctk.CTkFrame(proc_frame)
        proc_grid.pack(fill="x", padx=20, pady=10)
        
        # Auto approve threshold
        ctk.CTkLabel(proc_grid, text="Auto Approve Threshold:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.auto_approve_var = tk.StringVar(value="0.8")
        self.auto_approve_entry = ctk.CTkEntry(
            proc_grid,
            textvariable=self.auto_approve_var,
            width=100
        )
        self.auto_approve_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Processing delay
        ctk.CTkLabel(proc_grid, text="Processing Delay (sec):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.delay_var = tk.StringVar(value="0.5")
        self.delay_entry = ctk.CTkEntry(
            proc_grid,
            textvariable=self.delay_var,
            width=100
        )
        self.delay_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
    def setup_system_settings(self):
        """System settings section"""
        
        sys_frame = ctk.CTkFrame(self.tab_settings)
        sys_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            sys_frame,
            text="🔧 System Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Save/Load buttons
        button_frame = ctk.CTkFrame(sys_frame)
        button_frame.pack(pady=20)
        
        self.save_settings_btn = ctk.CTkButton(
            button_frame,
            text="[SAVE] Save Settings",
            command=self.save_settings
        )
        self.save_settings_btn.pack(side="left", padx=10)
        
        self.load_settings_btn = ctk.CTkButton(
            button_frame,
            text="[LOAD] Load Settings",
            command=self.load_settings
        )
        self.load_settings_btn.pack(side="left", padx=10)
        
        self.reset_settings_btn = ctk.CTkButton(
            button_frame,
            text="[REFRESH] Reset to Default",
            command=self.reset_settings
        )
        self.reset_settings_btn.pack(side="left", padx=10)
        
    # =========================================================================
    # LOGS TAB
    # =========================================================================
    
    def setup_logs_tab(self):
        """Logs viewing tab"""
        
        # Controls
        log_controls = ctk.CTkFrame(self.tab_logs, height=60)
        log_controls.pack(fill="x", padx=10, pady=10)
        log_controls.pack_propagate(False)
        
        self.refresh_logs_btn = ctk.CTkButton(
            log_controls,
            text="[REFRESH] Refresh Logs",
            command=self.refresh_logs
        )
        self.refresh_logs_btn.pack(side="left", padx=20, pady=15)
        
        self.clear_logs_btn = ctk.CTkButton(
            log_controls,
            text="[DEL] Clear Logs",
            command=self.clear_logs
        )
        self.clear_logs_btn.pack(side="left", padx=10, pady=15)
        
        # Log level selector
        ctk.CTkLabel(log_controls, text="Level:").pack(side="left", padx=20, pady=15)
        self.log_level_var = tk.StringVar(value="ALL")
        self.log_level_combo = ctk.CTkComboBox(
            log_controls,
            values=["ALL", "INFO", "ERROR", "WARNING", "DEBUG"],
            variable=self.log_level_var,
            width=100
        )
        self.log_level_combo.pack(side="left", padx=5, pady=15)
        
        # Log display
        self.logs_text = ctk.CTkTextbox(self.tab_logs)
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Load initial logs
        self.refresh_logs()
        
    # =========================================================================
    # STATUS BAR
    # =========================================================================
    
    def setup_status_bar(self):
        """Bottom status bar"""
        
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=5)
        self.status_bar.pack_propagate(False)
        
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_text.pack(side="left", padx=10, pady=5)
        
        # Right side info
        self.version_label = ctk.CTkLabel(
            self.status_bar,
            text="v2.0.0 | Claude API: Ready",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.pack(side="right", padx=10, pady=5)
        
    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def select_json_file(self):
        """Select JSON file for processing"""
        
        file_path = filedialog.askopenfilename(
            title="Select Prescription JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.json_file_var.set(os.path.basename(file_path))
            self.selected_json_file = file_path
            self.process_json_btn.configure(state="normal")
            self.update_status(f"Selected: {os.path.basename(file_path)}")
        
    def start_json_processing(self):
        """Start JSON file processing"""
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing already in progress!")
            return
        
        if not hasattr(self, 'selected_json_file'):
            messagebox.showerror("Error", "Please select a JSON file first!")
            return
        
        # Start processing in thread
        self.is_processing = True
        self.update_status("[REFRESH] Processing JSON file...")
        self.status_label.configure(text="[REFRESH] PROCESSING")
        
        self.processing_thread = threading.Thread(
            target=self.json_processing_worker
        )
        self.processing_thread.start()
        
    def json_processing_worker(self):
        """JSON processing worker thread"""
        
        try:
            # Initialize processor
            if not self.processor:
                self.processor = UnifiedPrescriptionProcessor()
            
            # Update UI
            self.root.after(0, lambda: self.json_progress_label.configure(text="Initializing processor..."))
            self.root.after(0, lambda: self.json_progress_bar.set(0.1))
            
            # Process file
            output_file = f"gui_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            self.root.after(0, lambda: self.json_progress_label.configure(text="Processing prescriptions..."))
            self.root.after(0, lambda: self.json_progress_bar.set(0.5))
            
            results = self.processor.process_from_json_file(
                self.selected_json_file, 
                output_file
            )
            
            # Update UI with results
            self.root.after(0, lambda: self.json_progress_bar.set(1.0))
            self.root.after(0, lambda: self.json_progress_label.configure(text="Processing completed!"))
            
            # Store results
            self.current_results = results
            self.processing_stats = self.processor.get_processing_stats()
            
            # Update UI
            self.root.after(0, self.update_results_display)
            self.root.after(0, self.update_json_stats)
            
            # Success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Processed {len(results)} prescriptions successfully!\nResults saved to: {output_file}"
            ))
            
        except Exception as e:
            # Error handling
            error_msg = f"Processing failed: {str(e)}"
            self.root.after(0, lambda: self.json_progress_label.configure(text="Processing failed!"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            print(f"Processing error: {e}")
            
        finally:
            # Reset UI state
            self.is_processing = False
            self.root.after(0, lambda: self.status_label.configure(text="[+] READY"))
            self.root.after(0, lambda: self.update_status("Processing completed"))
        
    def start_medula_processing(self):
        """Start live Medula processing"""
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing already in progress!")
            return
        
        # Get credentials
        username = self.medula_username_var.get().strip()
        password = self.medula_password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter Medula credentials!")
            return
        
        # Confirm CAPTCHA requirement
        if not messagebox.askyesno(
            "CAPTCHA Required", 
            "Medula login requires manual CAPTCHA solving.\n\nProceed with live processing?"
        ):
            return
        
        # Start processing
        self.is_processing = True
        self.update_status("[REFRESH] Connecting to Medula...")
        self.status_label.configure(text="[REFRESH] MEDULA")
        
        self.processing_thread = threading.Thread(
            target=self.medula_processing_worker
        )
        self.processing_thread.start()
        
    def medula_processing_worker(self):
        """Medula processing worker thread"""
        
        try:
            # Initialize processor
            if not self.processor:
                self.processor = UnifiedPrescriptionProcessor()
            
            # Update status
            self.root.after(0, lambda: self.medula_status_text.insert("end", "\\n[REFRESH] Initializing Medula connection..."))
            
            # Get parameters
            limit = int(self.medula_limit_var.get() or 5)
            group = self.medula_group_var.get()
            
            # Process
            self.root.after(0, lambda: self.medula_status_text.insert("end", f"\\n[NET] Processing {limit} prescriptions from Group {group}..."))
            
            results = self.processor.process_from_medula_live(limit=limit, group=group)
            
            # Store results
            self.current_results = results
            self.processing_stats = self.processor.get_processing_stats()
            
            # Update UI
            self.root.after(0, self.update_results_display)
            self.root.after(0, lambda: self.medula_status_text.insert("end", f"\\n[OK] Processing completed! {len(results)} prescriptions processed."))
            
            # Success
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Medula processing completed!\\nProcessed {len(results)} prescriptions."
            ))
            
        except Exception as e:
            # Error
            error_msg = f"Medula processing failed: {str(e)}"
            self.root.after(0, lambda: self.medula_status_text.insert("end", f"\\n[ERR] Error: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            # Reset state
            self.is_processing = False
            self.root.after(0, lambda: self.status_label.configure(text="[+] READY"))
            self.root.after(0, lambda: self.update_status("Medula processing completed"))
        
    def update_results_display(self):
        """Update results table display"""
        
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add new results
        for i, result in enumerate(self.current_results, 1):
            patient_name = result.get("patient_info", {}).get("name", "Unknown")
            processing_time = result.get("processing_metadata", {}).get("processing_time_seconds", 0)
            timestamp = result.get("processing_metadata", {}).get("timestamp", "")
            
            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp_str = dt.strftime("%H:%M:%S")
                except:
                    timestamp_str = timestamp[:19] if len(timestamp) > 19 else timestamp
            else:
                timestamp_str = ""
            
            self.results_tree.insert("", "end", values=(
                result.get("prescription_id", "N/A"),
                patient_name,
                result.get("final_decision", "unknown").upper(),
                result.get("sut_analysis", {}).get("action", "N/A").upper(),
                result.get("ai_analysis", {}).get("action", "N/A").upper(),
                f"{processing_time:.2f}s",
                timestamp_str
            ))
        
        # Update summary
        if self.current_results:
            total = len(self.current_results)
            approved = len([r for r in self.current_results if r.get("final_decision") == "approve"])
            rejected = len([r for r in self.current_results if r.get("final_decision") == "reject"])
            held = len([r for r in self.current_results if r.get("final_decision") == "hold"])
            
            summary = f"Total: {total} | Approved: {approved} | Rejected: {rejected} | Hold: {held}"
            self.results_summary_label.configure(text=summary)
            
            # Enable export
            self.export_btn.configure(state="normal")
        
    def update_json_stats(self):
        """Update JSON processing statistics"""
        
        if not self.processing_stats or not self.current_results:
            return
        
        stats_text = "[STATS] PROCESSING STATISTICS\\n"
        stats_text += "=" * 40 + "\\n"
        stats_text += f"Total Processed: {len(self.current_results)}\\n"
        stats_text += f"Approved: {self.processing_stats.get('approved', 0)}\\n"
        stats_text += f"Rejected: {self.processing_stats.get('rejected', 0)}\\n"
        stats_text += f"Hold: {self.processing_stats.get('held', 0)}\\n"
        stats_text += f"Errors: {self.processing_stats.get('errors', 0)}\\n\\n"
        
        # Processing times
        if self.processing_stats.get('start_time') and self.processing_stats.get('end_time'):
            start_time = self.processing_stats['start_time']
            end_time = self.processing_stats['end_time']
            
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
                
            total_time = (end_time - start_time).total_seconds()
            avg_time = total_time / len(self.current_results) if self.current_results else 0
            
            stats_text += f"Total Time: {total_time:.2f}s\\n"
            stats_text += f"Average per Prescription: {avg_time:.2f}s\\n\\n"
        
        # Claude API status
        claude_used = any(r.get("ai_analysis", {}).get("claude_used", False) for r in self.current_results)
        stats_text += f"Claude API Status: {'[OK] Active' if claude_used else '[ERR] Fallback'}\\n\\n"
        
        # Top issues
        stats_text += "🔍 COMMON ISSUES:\\n"
        issues = []
        for result in self.current_results:
            result_issues = result.get("details", {}).get("sut_issues", [])
            issues.extend(result_issues)
        
        if issues:
            from collections import Counter
            top_issues = Counter(issues).most_common(3)
            for issue, count in top_issues:
                stats_text += f"• {issue[:50]}... ({count}x)\\n"
        else:
            stats_text += "• No major issues found\\n"
        
        # Update text widget
        self.json_stats_text.delete("1.0", "end")
        self.json_stats_text.insert("1.0", stats_text)
        
    def export_results(self):
        """Export current results to file"""
        
        if not self.current_results:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        # Select export file
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                export_data = {
                    "metadata": {
                        "export_timestamp": datetime.now().isoformat(),
                        "total_results": len(self.current_results),
                        "processing_stats": self.processing_stats,
                        "exported_by": "GUI Unified Processor v2.0"
                    },
                    "results": self.current_results
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to:\\n{file_path}")
                self.update_status(f"Exported to {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
        
    def clear_results(self):
        """Clear current results"""
        
        if messagebox.askyesno("Confirm", "Clear all current results?"):
            self.current_results = []
            self.processing_stats = {}
            
            # Clear UI
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            self.results_summary_label.configure(text="No results available")
            self.json_stats_text.delete("1.0", "end")
            self.json_stats_text.insert("1.0", "No processing completed yet...")
            
            # Disable export
            self.export_btn.configure(state="disabled")
            
            self.update_status("Results cleared")
        
    def save_settings(self):
        """Save current settings"""
        
        try:
            settings_data = {
                "claude_api_key": self.claude_api_var.get(),
                "ai_provider": self.ai_provider_var.get(),
                "auto_approve_threshold": float(self.auto_approve_var.get()),
                "processing_delay": float(self.delay_var.get()),
                "medula_username": self.medula_username_var.get(),
                "saved_timestamp": datetime.now().isoformat()
            }
            
            with open("gui_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.update_status("Settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Save settings failed: {str(e)}")
        
    def load_settings(self):
        """Load settings from file and .env"""
        
        try:
            # Try to load from settings file
            if os.path.exists("gui_settings.json"):
                with open("gui_settings.json", 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                    
                self.claude_api_var.set(settings_data.get("claude_api_key", ""))
                self.ai_provider_var.set(settings_data.get("ai_provider", "claude"))
                self.auto_approve_var.set(str(settings_data.get("auto_approve_threshold", 0.8)))
                self.delay_var.set(str(settings_data.get("processing_delay", 0.5)))
                self.medula_username_var.set(settings_data.get("medula_username", ""))
            
            # Also load from .env if available
            try:
                from config.settings import Settings
                settings = Settings()
                
                if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                    self.claude_api_var.set(settings.ANTHROPIC_API_KEY)
                
                if hasattr(settings, 'medula_username') and settings.medula_username:
                    self.medula_username_var.set(settings.medula_username)
                    
            except:
                pass  # Ignore .env loading errors
            
            self.update_status("Settings loaded")
            
        except Exception as e:
            self.update_status(f"Load settings error: {str(e)}")
        
    def reset_settings(self):
        """Reset settings to default"""
        
        if messagebox.askyesno("Confirm", "Reset all settings to default values?"):
            self.claude_api_var.set("")
            self.ai_provider_var.set("claude")
            self.auto_approve_var.set("0.8")
            self.delay_var.set("0.5")
            self.medula_username_var.set("")
            self.medula_password_var.set("")
            self.medula_group_var.set("A")
            self.medula_limit_var.set("5")
            
            self.update_status("Settings reset to default")
        
    def refresh_logs(self):
        """Refresh log display"""
        
        try:
            log_file = "logs/eczane_otomasyon.log"
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                # Filter by level if needed
                level_filter = self.log_level_var.get()
                if level_filter != "ALL":
                    lines = log_content.split('\\n')
                    filtered_lines = [line for line in lines if level_filter in line]
                    log_content = '\\n'.join(filtered_lines[-100:])  # Last 100 matching lines
                else:
                    # Show last 200 lines
                    lines = log_content.split('\\n')
                    log_content = '\\n'.join(lines[-200:])
                
                self.logs_text.delete("1.0", "end")
                self.logs_text.insert("1.0", log_content)
                
            else:
                self.logs_text.delete("1.0", "end")
                self.logs_text.insert("1.0", "No log file found at: " + log_file)
                
        except Exception as e:
            self.logs_text.delete("1.0", "end")
            self.logs_text.insert("1.0", f"Error loading logs: {str(e)}")
        
    def clear_logs(self):
        """Clear log display"""
        
        if messagebox.askyesno("Confirm", "Clear log display?"):
            self.logs_text.delete("1.0", "end")
            self.logs_text.insert("1.0", "Logs cleared...")
        
    def update_status(self, message):
        """Update status bar"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.configure(text=f"[{timestamp}] {message}")
        
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def run(self):
        """Start the GUI application"""
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_status("Application started")
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing"""
        
        if self.is_processing:
            if not messagebox.askyesno("Confirm Exit", "Processing is in progress. Exit anyway?"):
                return
        
        # Cleanup
        if self.processor:
            try:
                self.processor._cleanup_browser()
            except:
                pass
        
        self.root.destroy()

# =========================================================================
# MAIN FUNCTION
# =========================================================================

def main():
    """Main function"""
    
    print("[*] Starting Unified Prescription Processor GUI...")
    
    try:
        # Create and run GUI
        app = UnifiedProcessorGUI()
        app.run()
        
    except Exception as e:
        print(f"[!] GUI startup error: {e}")
        messagebox.showerror("Startup Error", f"Failed to start GUI: {str(e)}")

if __name__ == "__main__":
    main()