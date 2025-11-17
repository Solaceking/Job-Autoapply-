"""
Minimal PySide6 prototype for Auto Job Applier
- Left navigation rail
- Top command bar
- Job Search form with language filter and "prefer English-first" option

This is a lightweight prototype to evaluate Qt workflow and UX.
"""
import sys

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except Exception as e:
    print("PySide6 is not installed. Install it with: pip install PySide6")
    raise


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Job Applier — Qt Prototype")
        self.resize(1100, 750)
        self._setup_ui()
        self._setup_statusbar()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left navigation (rail)
        nav = QtWidgets.QFrame()
        nav.setFixedWidth(84)
        nav.setFrameShape(QtWidgets.QFrame.StyledPanel)
        nav_layout = QtWidgets.QVBoxLayout(nav)
        nav_layout.setAlignment(QtCore.Qt.AlignTop)

        # Store navigation buttons for later reference
        self.nav_buttons = []
        
        for name in ("Dashboard", "Jobs", "Queue", "History", "AI", "Settings"):
            btn = QtWidgets.QPushButton(name)
            btn.setFixedSize(72, 48)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self._on_nav_clicked(n))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        # Set Dashboard as default active
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

        # Main content area
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)

        # Top toolbar
        toolbar = QtWidgets.QFrame()
        toolbar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        t_layout = QtWidgets.QHBoxLayout(toolbar)
        title = QtWidgets.QLabel("Auto Job Applier")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        t_layout.addWidget(title)
        t_layout.addStretch()
        run_btn = QtWidgets.QPushButton("Run")
        pause_btn = QtWidgets.QPushButton("Pause")
        stop_btn = QtWidgets.QPushButton("Stop")
        t_layout.addWidget(run_btn)
        t_layout.addWidget(pause_btn)
        t_layout.addWidget(stop_btn)

        # Job Search form
        form = QtWidgets.QGroupBox("Job Search")
        form_layout = QtWidgets.QGridLayout(form)

        form_layout.addWidget(QtWidgets.QLabel("Keywords:"), 0, 0)
        self.keywords_edit = QtWidgets.QLineEdit()
        form_layout.addWidget(self.keywords_edit, 0, 1)

        form_layout.addWidget(QtWidgets.QLabel("Location:"), 1, 0)
        self.location_edit = QtWidgets.QLineEdit()
        form_layout.addWidget(self.location_edit, 1, 1)

        form_layout.addWidget(QtWidgets.QLabel("Language:"), 2, 0)
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(["", "English", "Spanish", "French", "German", "Portuguese", "Hindi", "Chinese"])
        self.language_combo.setCurrentText("English")
        form_layout.addWidget(self.language_combo, 2, 1)

        self.pref_english_chk = QtWidgets.QCheckBox("Prefer English-first jobs")
        self.pref_english_chk.setChecked(True)
        form_layout.addWidget(self.pref_english_chk, 3, 1)

        self.easy_apply_chk = QtWidgets.QCheckBox("Easy Apply only")
        self.easy_apply_chk.setChecked(True)
        form_layout.addWidget(self.easy_apply_chk, 4, 1)

        self.max_apply_spin = QtWidgets.QSpinBox()
        self.max_apply_spin.setRange(1, 1000)
        self.max_apply_spin.setValue(30)
        form_layout.addWidget(QtWidgets.QLabel("Max Applications:"), 5, 0)
        form_layout.addWidget(self.max_apply_spin, 5, 1)

        search_btn = QtWidgets.QPushButton("Search & Apply")
        form_layout.addWidget(search_btn, 6, 0, 1, 2)

        # logs area
        logs = QtWidgets.QGroupBox("Logs")
        logs_layout = QtWidgets.QVBoxLayout(logs)
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        logs_layout.addWidget(self.log_text)

        content_layout.addWidget(toolbar)
        content_layout.addWidget(form)
        
        # Progress section
        progress_box = QtWidgets.QGroupBox("Progress")
        progress_layout = QtWidgets.QVBoxLayout(progress_box)
        
        # Application count display
        stats_layout = QtWidgets.QHBoxLayout()
        self.applied_label = QtWidgets.QLabel("Applied: 0")
        self.failed_label = QtWidgets.QLabel("Failed: 0")
        self.skipped_label = QtWidgets.QLabel("Skipped: 0")
        self.current_job_label = QtWidgets.QLabel("Current: —")
        stats_layout.addWidget(self.applied_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.skipped_label)
        stats_layout.addWidget(self.current_job_label)
        stats_layout.addStretch()
        progress_layout.addLayout(stats_layout)
        
        # Overall progress bar
        overall_layout = QtWidgets.QHBoxLayout()
        overall_layout.addWidget(QtWidgets.QLabel("Overall:"))
        self.overall_progress = QtWidgets.QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        overall_layout.addWidget(self.overall_progress)
        progress_layout.addLayout(overall_layout)
        
        # Form fill progress bar
        form_layout_prog = QtWidgets.QHBoxLayout()
        form_layout_prog.addWidget(QtWidgets.QLabel("Form Fill:"))
        self.form_progress = QtWidgets.QProgressBar()
        self.form_progress.setRange(0, 100)
        self.form_progress.setValue(0)
        form_layout_prog.addWidget(self.form_progress)
        progress_layout.addLayout(form_layout_prog)
        
        content_layout.addWidget(progress_box)
        content_layout.addWidget(logs)
        content_layout.addStretch()

        main_layout.addWidget(nav)
        main_layout.addWidget(content, 1)

        self.setCentralWidget(central)

        # connect
        search_btn.clicked.connect(self._on_search)
        run_btn.clicked.connect(lambda: self._log("info", "Run pressed"))
        pause_btn.clicked.connect(lambda: self._log("warning", "Pause pressed"))
        stop_btn.clicked.connect(self._on_stop)

        # Worker reference
        self.worker = None

        # CAPTCHA banner (hidden by default). Non-modal banner with Resume/Cancel.
        self.captcha_banner = QtWidgets.QFrame()
        self.captcha_banner.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.captcha_banner.setStyleSheet("background-color: #FFF4E5; border: 1px solid #E6B800;")
        banner_layout = QtWidgets.QHBoxLayout(self.captcha_banner)
        self.captcha_label = QtWidgets.QLabel("")
        banner_layout.addWidget(self.captcha_label)
        banner_layout.addStretch()
        self.captcha_resume_btn = QtWidgets.QPushButton("Resume")
        self.captcha_cancel_btn = QtWidgets.QPushButton("Cancel")
        banner_layout.addWidget(self.captcha_resume_btn)
        banner_layout.addWidget(self.captcha_cancel_btn)
        self.captcha_banner.setVisible(False)
        # add banner at top of content layout so it's visible while automation runs
        content_layout.insertWidget(0, self.captcha_banner)

        # Connect banner buttons
        self.captcha_resume_btn.clicked.connect(self._on_captcha_resume_clicked)
        self.captcha_cancel_btn.clicked.connect(self._on_captcha_cancel_clicked)
    def _setup_statusbar(self):
        """Setup status bar with elapsed time and performance metrics."""
        self.statusbar_label = QtWidgets.QLabel("Ready")
        self.statusBar().addWidget(self.statusbar_label)
    
    def _on_nav_clicked(self, nav_name: str):
        """Handle navigation button clicks."""
        # Uncheck all other navigation buttons
        for btn in self.nav_buttons:
            if btn.text() != nav_name:
                btn.setChecked(False)
        
        # Log the navigation
        self._log("info", f"Navigated to: {nav_name}")
        self.statusbar_label.setText(f"View: {nav_name}")
        
        # Show message about feature
        if nav_name in ("Queue", "History"):
            self._log("info", f"{nav_name} feature coming soon!")
        elif nav_name == "AI":
            self._log("info", "AI settings: Configure in config/secrets.py")
        elif nav_name == "Settings":
            self._log("info", "Settings: Edit config/settings.py and config/search.py")
        elif nav_name == "Jobs":
            self._log("info", "Jobs view: Use Search & Apply to start finding jobs")

    def _on_stop(self):
        self._log("warning", "Stop requested by user")
        # Best-effort: close browser to interrupt automation
        try:
            from modules.automation_manager import request_cancel_current
            cancelled = request_cancel_current()
            if cancelled:
                self._log("info", "Requested cooperative cancellation")
            else:
                # fallback to close browser
                from modules.open_chrome import close_browser
                close_browser()
                self._log("info", "Requested browser close (fallback)")
        except Exception as e:
            self._log("error", f"Error requesting stop: {e}")

    def _log(self, level: str, msg: str):
        self.log_text.append(f"[{level.upper()}] {msg}")

    def _on_search(self):
        keywords = self.keywords_edit.text()
        location = self.location_edit.text()
        language = self.language_combo.currentText()
        prefer_english = self.pref_english_chk.isChecked()
        easy_apply = self.easy_apply_chk.isChecked()
        max_apps = self.max_apply_spin.value()

        self._log("info", f"Search: keywords='{keywords}' location='{location}' language='{language}' prefer_english={prefer_english} easy_apply={easy_apply} max={max_apps}")

        # Start background worker to run automation
        if self.worker and self.worker.isRunning():
            self._log("warning", "Automation already running")
            return

        # Prepare form_data minimally (could be extended to collect more fields)
        form_data = {}

        # persist the search settings
        try:
            from modules.settings_manager import save_search_settings
            save_search_settings({
                "search_terms": [s.strip() for s in keywords.split(",") if s.strip()],
                "search_location": location,
                "preferred_language": language,
                "prefer_english_first": prefer_english,
                "easy_apply_only": easy_apply,
                "switch_number": max_apps,
            })
            self._log("debug", "Search settings saved")
        except Exception as e:
            self._log("error", f"Failed to save settings: {e}")

        self.worker = AutomationWorker(
            job_title=keywords,
            location=location,
            max_applications=max_apps,
            form_data=form_data,
            language=language,
            prefer_english=prefer_english
        )
        self.worker.log_signal.connect(lambda lvl, msg: self._log(lvl, msg))
        self.worker.captcha_pause_signal.connect(self._on_captcha_pause)
        self.worker.progress_signal.connect(self._on_worker_progress)
        self.worker.form_progress_signal.connect(self._on_form_progress)
        self.worker.finished_signal.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_finished(self, stats: dict):
        self._log("success", f"Automation finished: {stats}")
        self.overall_progress.setValue(100)
        self.statusbar_label.setText(f"Complete — Applied: {stats.get('applied', 0)}, Failed: {stats.get('failed', 0)}, Skipped: {stats.get('skipped', 0)}")

    def _on_worker_progress(self, applied: int, failed: int, skipped: int, current_job: str):
        """Update progress labels and overall progress bar."""
        self.applied_label.setText(f"Applied: {applied}")
        self.failed_label.setText(f"Failed: {failed}")
        self.skipped_label.setText(f"Skipped: {skipped}")
        self.current_job_label.setText(f"Current: {current_job[:40]}")
        
        # Update overall progress (rough estimate based on total so far)
        total = applied + failed + skipped
        if total > 0:
            progress_pct = min(int((total / max(self.max_apply_spin.value(), 1)) * 100), 99)
            self.overall_progress.setValue(progress_pct)
            self.statusbar_label.setText(f"Processing... Applied: {applied} | Failed: {failed} | Skipped: {skipped}")

    def _on_form_progress(self, pct: int):
        """Update form fill progress bar (0-100%)."""
        self.form_progress.setValue(pct)
    def _on_captcha_pause(self, message: str):
        """Handle CAPTCHA pause notification from worker.

        Show a non-modal banner with Resume/Cancel and update status bar. The banner
        allows the user to solve CAPTCHA in the browser and press Resume.
        """
        try:
            # Update banner text and make visible
            msg = message or "CAPTCHA detected. Please solve the CAPTCHA in the browser window."
            # Ensure banner exists (in case called earlier than UI setup)
            try:
                self.captcha_label.setText(msg)
                self.captcha_banner.setVisible(True)
            except Exception:
                # If any issue with banner, fallback to modal dialog
                dlg = QtWidgets.QMessageBox(self)
                dlg.setIcon(QtWidgets.QMessageBox.Warning)
                dlg.setWindowTitle("CAPTCHA detected — Action required")
                dlg.setText("CAPTCHA detected during automation. Please solve the CAPTCHA in the browser window, then press Resume.")
                if message:
                    dlg.setInformativeText(message)
                resume_btn = dlg.addButton("Resume", QtWidgets.QMessageBox.AcceptRole)
                cancel_btn = dlg.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
                dlg.setDefaultButton(resume_btn)
                dlg.exec()
                if dlg.clickedButton() == resume_btn:
                    try:
                        from modules.error_recovery import request_resume
                        request_resume()
                        self._log("info", "User requested resume after CAPTCHA")
                    except Exception as e:
                        self._log("error", f"Failed to request resume: {e}")
                else:
                    self._log("warning", "User cancelled resume after CAPTCHA")

            self.statusbar_label.setText("Paused — CAPTCHA detected")
            self._log("warning", f"CAPTCHA paused: {msg}")
        except Exception as e:
            self._log("error", f"Error showing CAPTCHA banner: {e}")

    def _on_captcha_resume_clicked(self):
        """User clicked Resume on the banner; signal recovery manager and hide banner."""
        try:
            from modules.error_recovery import request_resume
            ok = request_resume()
            if ok:
                self._log("info", "User requested resume after CAPTCHA")
            else:
                self._log("warning", "Resume requested but no recovery manager present")
        except Exception as e:
            self._log("error", f"Failed to request resume: {e}")
        finally:
            try:
                self.captcha_banner.setVisible(False)
                self.statusbar_label.setText("Resuming...")
            except Exception:
                pass

    def _on_captcha_cancel_clicked(self):
        """User clicked Cancel on banner; hide banner and leave manager to timeout or handle."""
        try:
            self.captcha_banner.setVisible(False)
            self.statusbar_label.setText("Automation paused (user cancelled resume)")
            self._log("warning", "User cancelled resume after CAPTCHA")
        except Exception as e:
            self._log("error", f"Error handling CAPTCHA cancel: {e}")


class AutomationWorker(QtCore.QThread):
    """Background worker that runs the LinkedIn automation workflow."""

    log_signal = QtCore.Signal(str, str)  # level, message
    finished_signal = QtCore.Signal(dict)
    progress_signal = QtCore.Signal(int, int, int, str)  # applied, failed, skipped, current_job
    form_progress_signal = QtCore.Signal(int)  # form fill percentage (0-100)
    captcha_pause_signal = QtCore.Signal(str)  # message when CAPTCHA pause required

    def __init__(self, job_title: str, location: str, max_applications: int, form_data: dict, language: str = "", prefer_english: bool = False):
        super().__init__()
        self.job_title = job_title
        self.location = location
        self.max_applications = max_applications
        self.form_data = form_data
        self.language = language
        self.prefer_english = prefer_english

    def emit_log(self, message: str, level: str = "info"):
        try:
            self.log_signal.emit(level, message)
        except Exception:
            pass

    def run(self):
        try:
            # Open browser
            from modules.open_chrome import open_browser, close_browser, driver, wait, actions
            from modules.automation_manager import LinkedInSession

            self.emit_log("Opening browser...", "info")
            open_browser()

            # Wait for globals to be set
            d = driver
            w = wait
            a = actions

            if not d or not w:
                self.emit_log("Browser failed to initialize", "error")
                self.finished_signal.emit({})
                return

            session = LinkedInSession(d, w, a, log_callback=self.emit_log)
            
            # Wire progress callbacks to automation manager (use app_manager attribute)
            def on_progress(applied, failed, skipped, current_job):
                try:
                    self.progress_signal.emit(applied, failed, skipped, current_job)
                except Exception:
                    pass

            def on_form_progress(pct: int):
                try:
                    self.form_progress_signal.emit(pct)
                except Exception:
                    pass

            # app_manager is the JobApplicationManager instance on LinkedInSession
            try:
                session.app_manager.progress_callback = on_progress
                session.app_manager.form_progress_callback = on_form_progress
            except Exception:
                # backward compatibility: try older attribute name if present
                try:
                    session.job_manager.progress_callback = on_progress
                    session.job_manager.form_progress_callback = on_form_progress
                except Exception:
                    pass

            # If an ErrorRecoveryManager is present, enable blocking captcha wait and
            # set a callback that will emit a signal to the UI to request user action.
            try:
                from modules import error_recovery
                mgr = getattr(error_recovery, 'current_recovery_manager', None)
                if mgr:
                    try:
                        mgr.config.captcha_blocking_wait = True
                        mgr.config.captcha_pause_callback = lambda msg: self.captcha_pause_signal.emit(msg or "CAPTCHA detected")
                        # keep reference for debugging if needed
                        self.recovery_manager = mgr
                    except Exception:
                        pass
            except Exception:
                pass

            # Use defaults for credentials from config if available (login optional)
            stats = session.run_search_and_apply(
                self.job_title,
                self.location,
                self.max_applications,
                self.form_data,
                language=self.language,
                prefer_english=self.prefer_english,
            )

            self.finished_signal.emit(stats)

        except Exception as e:
            self.emit_log(f"Worker exception: {e}", "error")
            try:
                close_browser()
            except Exception:
                pass
            self.finished_signal.emit({"error": str(e)})


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
