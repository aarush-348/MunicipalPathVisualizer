/**
 * Main Civic Task Navigator Application Controller
 * Grounded in Civic Functionalism & Municipal Ledger discipline.
 * 100% Data-Driven & Decoupled Architecture across Maharashtra Municipalities
 * Conforming to GIGW 3.0 / S3WaaS and Stitch Design standards.
 */

const TRANSLATIONS = {
    en: {
        find_service: "Find Service",
        step_roadmap: "Step Roadmap",
        step_details: "Step Details & Apply",
        my_progress: "My Progress",
        admin: "Admin",
        critical_path: "Highlight Critical Path",
        share_route: "Share Route",
        track_app_heading: "Track Existing Application Status",
        track_btn: "Check Status on Official Portal ↗"
    },
    mr: {
        find_service: "सेवा शोधा",
        step_roadmap: "प्रक्रिया मार्ग",
        step_details: "तपशील व अर्ज",
        my_progress: "माझी प्रगती",
        admin: "प्रशासन",
        critical_path: "महत्त्वाचा मार्ग दाखवा",
        share_route: "मार्ग सामायिक करा",
        track_app_heading: "तुमच्या अर्जाची सद्यस्थिती तपासा",
        track_btn: "अधिकृत पोर्टलवर स्थिती तपासा ↗"
    }
};

class CivicApp {
    constructor() {
        this.currentTaskId = 'task-mah-small-biz';
        this.currentTask = null;
        this.currentRoadmap = null;
        this.selectedStationId = null;
        
        // Active view tabs & visual modes
        this.activeTab = 'task-lookup';
        this.wayfindingMode = 'subway'; // 'subway' | 'dag'
        this.criticalPathActive = false;
        this.activeDocCategory = 'all';

        // Language state
        this.currentLang = localStorage.getItem('civic_lang') || 'en';

        // Scoped progress & document state (will be loaded per-task)
        this.completedStepIds = new Set();
        this.inProgressStepIds = new Set();
        this.checkedDocIds = new Set();
        this.stepApplicationNumbers = {};

        // All catalog tasks cache
        this.allTasks = [];
        this.lastSearchNotice = null;

        // Accessibility font sizing state
        this.fontSizes = ['font-size-sm', 'font-size-md', 'font-size-lg', 'font-size-xl'];
        this.currentFontSizeIdx = 1; // Default medium (15px)

        this._init();
    }

    async _init() {
        this._bindNavigationEvents();
        this._bindUiEvents();

        // Initialize SVG DAG visualizer
        this.visualizer = new CivicGraphVisualizer('graph-canvas', (nodeId) => {
            this.selectStation(nodeId);
        });

        // Initialize Dynamic Subway Transit Renderer
        if (typeof CivicSubwayRenderer !== 'undefined') {
            this.subwayRenderer = new CivicSubwayRenderer('subway-transit-svg', (nodeId) => {
                this.selectStation(nodeId);
            });
        }

        // Initialize Admin manager
        if (typeof CivicAdminManager !== 'undefined') {
            this.admin = new CivicAdminManager(this);
            window.adminManager = this.admin;
        }

        // Check URL parameters or hash for deep linking
        const initialHash = window.location.hash.replace('#', '');
        const urlParams = new URLSearchParams(window.location.search);
        const taskParam = urlParams.get('task') || (initialHash.startsWith('task-') ? initialHash : null);

        if (taskParam) {
            this.currentTaskId = taskParam;
            this.activeTab = 'roadmap-and-route';
        } else if (initialHash && ['task-lookup', 'roadmap-and-route', 'step-dossier', 'document-locker', 'citizen-ledger', 'registry-admin'].includes(initialHash)) {
            this.activeTab = initialHash;
        }

        // 1. Fetch available catalog tasks
        await this.loadTasksList();

        // 2. Load initial scoped task state & roadmap
        await this.loadTaskAndRoute(this.currentTaskId);

        // 3. Switch to initial tab
        this.switchNavTab(this.activeTab);

        // 4. Apply initial language translation
        this.applyTranslations();
    }

    // -------------------------------------------------------------------------
    // Navigation & UI Events Binding
    // -------------------------------------------------------------------------
    _bindNavigationEvents() {
        document.querySelectorAll('#top-nav-tabs .nav-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const path = btn.getAttribute('data-path');
                this.switchNavTab(path);
            });
        });

        window.addEventListener('hashchange', () => {
            const h = window.location.hash.replace('#', '');
            if (h && h !== this.activeTab) {
                this.switchNavTab(h);
            }
        });

        // Keyboard shortcuts: '/' focuses search, 'ESC' closes drawer
        window.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                this.switchNavTab('task-lookup');
                const inp = document.getElementById('taskQuery');
                if (inp) inp.focus();
            } else if (e.key === 'Escape') {
                this.closeDrawer();
            }
        });
    }

    _bindUiEvents() {
        // Drawer backdrop & close button
        const btnClose = document.getElementById('btn-close-drawer');
        const backdrop = document.getElementById('drawer-backdrop');
        if (btnClose) btnClose.addEventListener('click', () => this.closeDrawer());
        if (backdrop) backdrop.addEventListener('click', () => this.closeDrawer());

        // Drawer complete toggle
        const btnToggleComplete = document.getElementById('btn-toggle-complete');
        if (btnToggleComplete) {
            btnToggleComplete.addEventListener('click', () => {
                if (this.selectedStationId) {
                    this.toggleStepCompletion(this.selectedStationId);
                }
            });
        }

        // DAG Canvas tools
        const btnZoomIn = document.getElementById('btn-zoom-in');
        const btnZoomOut = document.getElementById('btn-zoom-out');
        const btnFit = document.getElementById('btn-fit-screen');
        const btnReset = document.getElementById('btn-reset-view');

        if (btnZoomIn) btnZoomIn.addEventListener('click', () => this.visualizer.zoomIn());
        if (btnZoomOut) btnZoomOut.addEventListener('click', () => this.visualizer.zoomOut());
        if (btnFit) btnFit.addEventListener('click', () => this.visualizer.fitToScreen());
        if (btnReset) btnReset.addEventListener('click', () => this.visualizer.resetView());
    }

    // -------------------------------------------------------------------------
    // Per-Task Scoped State Management & Lifecycle
    // -------------------------------------------------------------------------
    loadTaskScopedState(taskId) {
        this.currentTaskId = taskId;

        // 1. Completed Steps
        const savedCompleted = localStorage.getItem(`civic_completed_steps_${taskId}`);
        if (savedCompleted) {
            try {
                this.completedStepIds = new Set(JSON.parse(savedCompleted));
            } catch (e) {
                this.completedStepIds = new Set();
            }
        } else {
            this.completedStepIds = new Set();
        }

        // 2. In-Progress Steps
        const savedInProgress = localStorage.getItem(`civic_inprogress_steps_${taskId}`);
        if (savedInProgress) {
            try {
                this.inProgressStepIds = new Set(JSON.parse(savedInProgress));
            } catch (e) {
                this.inProgressStepIds = new Set();
            }
        } else {
            this.inProgressStepIds = new Set();
        }

        // 3. Station Application / Challan Numbers Mapping
        const savedAppNums = localStorage.getItem(`civic_station_app_nums_${taskId}`);
        if (savedAppNums) {
            try {
                this.stepApplicationNumbers = JSON.parse(savedAppNums);
            } catch (e) {
                this.stepApplicationNumbers = {};
            }
        } else {
            this.stepApplicationNumbers = {};
        }

        // 4. User Checked Document Bag (with universal identity document carry-over)
        const savedDocs = localStorage.getItem(`civic_user_docs_${taskId}`);
        if (savedDocs) {
            try {
                this.checkedDocIds = new Set(JSON.parse(savedDocs));
            } catch (e) {
                this.checkedDocIds = new Set();
            }
        } else {
            // Find any standard KYC identity docs the citizen already marked in any previous task
            const universalKeywords = ["aadhaar", "pan", "passport", "incorporation", "electricity bill", "lease agreement", "rent agreement"];
            const carryOver = new Set();
            try {
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith('civic_user_docs_')) {
                        const parsed = JSON.parse(localStorage.getItem(key) || '[]');
                        parsed.forEach(docName => {
                            const lower = (docName || '').toLowerCase();
                            if (universalKeywords.some(kw => lower.includes(kw))) {
                                carryOver.add(docName);
                            }
                        });
                    }
                }
            } catch (e) {}

            this.checkedDocIds = carryOver;
            this.saveTaskDocs();
        }
    }

    saveTaskCompleted() {
        localStorage.setItem(`civic_completed_steps_${this.currentTaskId}`, JSON.stringify(Array.from(this.completedStepIds)));
        this.syncProgressToBackend();
    }

    saveTaskInProgress() {
        localStorage.setItem(`civic_inprogress_steps_${this.currentTaskId}`, JSON.stringify(Array.from(this.inProgressStepIds)));
        this.syncProgressToBackend();
    }

    async syncProgressToBackend() {
        if (!this.currentTaskId) return;
        try {
            await fetch('/api/user/progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'citizen_session',
                    task_id: this.currentTaskId,
                    completed_step_ids: Array.from(this.completedStepIds),
                    in_progress_step_ids: Array.from(this.inProgressStepIds)
                })
            });
        } catch (e) {
            // Local fallback active
        }
    }

    saveTaskDocs() {
        localStorage.setItem(`civic_user_docs_${this.currentTaskId}`, JSON.stringify(Array.from(this.checkedDocIds)));
    }

    saveTaskAppNums() {
        localStorage.setItem(`civic_station_app_nums_${this.currentTaskId}`, JSON.stringify(this.stepApplicationNumbers));
    }

    // GIGW Accessibility: Font Resizer
    adjustFontSize(action) {
        const body = document.body;
        this.fontSizes.forEach(cls => body.classList.remove(cls));

        if (action === 'increase') {
            this.currentFontSizeIdx = Math.min(this.fontSizes.length - 1, this.currentFontSizeIdx + 1);
        } else if (action === 'decrease') {
            this.currentFontSizeIdx = Math.max(0, this.currentFontSizeIdx - 1);
        } else {
            this.currentFontSizeIdx = 1; // Default
        }

        body.classList.add(this.fontSizes[this.currentFontSizeIdx]);
    }

    // GIGW Accessibility: High Contrast Toggle
    toggleHighContrast() {
        document.body.classList.toggle('high-contrast');
    }

    // -------------------------------------------------------------------------
    // Bilingual (EN | मराठी) Language Engine
    // -------------------------------------------------------------------------
    toggleLanguage() {
        this.currentLang = (this.currentLang === 'en') ? 'mr' : 'en';
        localStorage.setItem('civic_lang', this.currentLang);
        this.applyTranslations();
    }

    getTaskTitle(t) {
        if (!t) return '';
        if (this.currentLang === 'mr' && window.TASK_TRANSLATIONS && window.TASK_TRANSLATIONS[t.id] && window.TASK_TRANSLATIONS[t.id].title) {
            return window.TASK_TRANSLATIONS[t.id].title;
        }
        return t.title || '';
    }

    getTaskDesc(t) {
        if (!t) return '';
        if (this.currentLang === 'mr' && window.TASK_TRANSLATIONS && window.TASK_TRANSLATIONS[t.id] && window.TASK_TRANSLATIONS[t.id].description) {
            return window.TASK_TRANSLATIONS[t.id].description;
        }
        return t.description || '';
    }

    getTaskMunicipality(t) {
        if (!t) return '';
        if (this.currentLang === 'mr') {
            if (window.TASK_TRANSLATIONS && window.TASK_TRANSLATIONS[t.id] && window.TASK_TRANSLATIONS[t.id].municipality) {
                return window.TASK_TRANSLATIONS[t.id].municipality;
            }
            if (window.MUNI_TRANSLATIONS && window.MUNI_TRANSLATIONS[t.municipality]) {
                return window.MUNI_TRANSLATIONS[t.municipality];
            }
        }
        return t.municipality || '';
    }

    getTaskCategory(t) {
        if (!t) return '';
        if (this.currentLang === 'mr' && window.TASK_TRANSLATIONS && window.TASK_TRANSLATIONS[t.id] && window.TASK_TRANSLATIONS[t.id].category) {
            return window.TASK_TRANSLATIONS[t.id].category;
        }
        return t.category || '';
    }

    getStepTitle(step, taskId) {
        if (!step) return '';
        const tId = taskId || (this.currentTask && this.currentTask.id);
        if (this.currentLang === 'mr' && window.TASK_TRANSLATIONS) {
            if (tId && window.TASK_TRANSLATIONS[tId]?.steps?.[step.id]?.title) {
                return window.TASK_TRANSLATIONS[tId].steps[step.id].title;
            }
            // Fallback: search all tasks for this step ID
            for (const tKey of Object.keys(window.TASK_TRANSLATIONS)) {
                if (window.TASK_TRANSLATIONS[tKey]?.steps?.[step.id]?.title) {
                    return window.TASK_TRANSLATIONS[tKey].steps[step.id].title;
                }
            }
        }
        return step.title || '';
    }

    getStepDesc(step, taskId) {
        if (!step) return '';
        const tId = taskId || (this.currentTask && this.currentTask.id);
        if (this.currentLang === 'mr' && window.TASK_TRANSLATIONS) {
            if (tId && window.TASK_TRANSLATIONS[tId]?.steps?.[step.id]?.description) {
                return window.TASK_TRANSLATIONS[tId].steps[step.id].description;
            }
            // Fallback: search all tasks for this step ID
            for (const tKey of Object.keys(window.TASK_TRANSLATIONS)) {
                if (window.TASK_TRANSLATIONS[tKey]?.steps?.[step.id]?.description) {
                    return window.TASK_TRANSLATIONS[tKey].steps[step.id].description;
                }
            }
        }
        return step.description || '';
    }

    getStepDept(step, taskId) {
        if (!step) return '';
        const tId = taskId || (this.currentTask && this.currentTask.id);
        if (this.currentLang === 'mr' && window.TASK_TRANSLATIONS) {
            if (tId && window.TASK_TRANSLATIONS[tId]?.steps?.[step.id]?.department) {
                return window.TASK_TRANSLATIONS[tId].steps[step.id].department;
            }
            // Fallback: search all tasks for this step ID
            for (const tKey of Object.keys(window.TASK_TRANSLATIONS)) {
                if (window.TASK_TRANSLATIONS[tKey]?.steps?.[step.id]?.department) {
                    return window.TASK_TRANSLATIONS[tKey].steps[step.id].department;
                }
            }
        }
        return (step.department && step.department.name) || step.department_name || (typeof step.department === 'string' ? step.department : '') || '';
    }

    getDocName(docName) {
        if (!docName) return '';
        if (this.currentLang === 'mr' && window.DOC_TRANSLATIONS) {
            if (window.DOC_TRANSLATIONS[docName]) {
                return window.DOC_TRANSLATIONS[docName];
            }
            const lower = docName.toLowerCase();
            for (const [key, val] of Object.entries(window.DOC_TRANSLATIONS)) {
                if (lower.includes(key.toLowerCase())) {
                    return val;
                }
            }
        }
        return docName;
    }

    applyTranslations() {
        const lang = this.currentLang;
        const isMr = (lang === 'mr');

        // 1. Language Toggle Button Label
        const btnToggle = document.getElementById('label-lang-toggle');
        if (btnToggle) {
            btnToggle.innerText = isMr ? 'English' : 'मराठी';
        }

        // 2. HTML Lang attribute & Document Title
        document.documentElement.lang = lang;
        document.title = isMr
            ? "नागरिक कार्य मार्गदर्शक | महाराष्ट्र शासन नागरिक सेवा मार्गदर्शिका"
            : "Civic Task Navigator | Government of Maharashtra Citizen Services Guide";

        // 3. Translate all elements with [data-i18n]
        const uiDict = (window.UI_STRINGS && window.UI_STRINGS[lang]) || (window.UI_STRINGS && window.UI_STRINGS.en) || {};
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (uiDict[key]) {
                el.innerText = uiDict[key];
            }
        });

        // 4. Update search input placeholder
        const taskInp = document.getElementById('taskQuery');
        if (taskInp) {
            taskInp.placeholder = isMr
                ? "उदा. मला दुकान नोंदणी करायची आहे, किंवा सातबारा फेरफार अर्ज"
                : "e.g. I want to register a small business, or Apply for 7/12 land extract";
        }

        // 5. Update Applicant Type Dropdown options
        const entSelect = document.getElementById('entityClassification');
        if (entSelect) {
            const applicantOptions = [
                { val: "sole-prop", en: "Individual Citizen / Sole Proprietor (एकल नागरिक / व्यापारी)", mr: "एकल नागरिक / व्यापारी (Individual / Sole Proprietor)" },
                { val: "commercial-pvt", en: "Private Limited Company / LLP", mr: "प्रायव्हेट लिमिटेड कंपनी / एलएलपी (Pvt Ltd / LLP)" },
                { val: "partnership", en: "Partnership Firm (भागीदारी संस्था)", mr: "भागीदारी संस्था (Partnership Firm)" },
                { val: "individual-citizen", en: "Student / Resident (दाखला व प्रमाणपत्रे)", mr: "विद्यार्थी / रहिवासी (दाखले व प्रमाणपत्रे)" },
                { val: "chs", en: "Cooperative Housing Society (CHS)", mr: "सहकारी गृहनिर्माण संस्था (Co-op Housing Society)" }
            ];
            const currentVal = entSelect.value;
            entSelect.innerHTML = applicantOptions.map(opt => `
                <option value="${opt.val}" ${opt.val === currentVal ? 'selected' : ''}>${isMr ? opt.mr : opt.en}</option>
            `).join('');
        }

        // 6. Update Tracker Portal Select options
        const trackPortalSelect = document.getElementById('select-track-portal');
        if (trackPortalSelect) {
            const portalOptions = [
                { val: "aaple_sarkar", en: "Aaple Sarkar RTS Tracking (Statewide)", mr: "आपले सरकार RTS ट्रॅकिंग (महाराष्ट्र राज्यव्यापी)" },
                { val: "mcgm", en: "MCGM / BMC Citizen Portal (Mumbai)", mr: "बीएमसी / MCGM नागरिक पोर्टल (मुंबई)" },
                { val: "mahabhumi", en: "MahaBhumi Bhulekh / 7/12 Mutation (Statewide)", mr: "महाभूमी भुलेख / ७/१२ फेरफार (महाराष्ट्र)" },
                { val: "foscos", en: "FoSCoS Food Safety License (FSSAI)", mr: "अन्न सुरक्षा व मानके परवाना (FSSAI FoSCoS)" }
            ];
            const currentVal = trackPortalSelect.value;
            trackPortalSelect.innerHTML = portalOptions.map(opt => `
                <option value="${opt.val}" ${opt.val === currentVal ? 'selected' : ''}>${isMr ? opt.mr : opt.en}</option>
            `).join('');
        }

        // 7. Update Jurisdiction dropdowns
        this.populateJurisdictionDropdowns();

        // 8. Re-render Dynamic Views
        this.renderTasksCatalog();
        if (this.currentTask) {
            this.updateHeaderAndStats();
            this.renderRoadmapStepCards();
            this.updateStationUI();
            this.renderCitizenLedger();

            if (this.subwayRenderer && this.currentRoadmap) {
                this.subwayRenderer.render(
                    this.currentTask,
                    this.currentRoadmap,
                    this.completedStepIds,
                    this.selectedStationId
                );
            }
            if (this.visualizer && this.currentRoadmap) {
                this.visualizer.setRoadmapData(this.currentRoadmap);
            }
        }

        if (this.admin && typeof this.admin.renderModerationQueue === 'function') {
            this.admin.renderModerationQueue();
        }
    }

    // -------------------------------------------------------------------------
    // Share Route & WhatsApp Summary Engine
    // -------------------------------------------------------------------------
    openShareModal() {
        const modal = document.getElementById('share-modal');
        const input = document.getElementById('share-link-input');
        const toast = document.getElementById('share-toast');
        if (toast) toast.classList.add('hidden');

        if (input && this.currentTaskId) {
            input.value = `${window.location.origin}/?task=${this.currentTaskId}`;
        }
        if (modal) modal.style.display = 'flex';
    }

    closeShareModal() {
        const modal = document.getElementById('share-modal');
        if (modal) modal.style.display = 'none';
    }

    copyShareLink() {
        const input = document.getElementById('share-link-input');
        const toast = document.getElementById('share-toast');
        if (!input) return;

        input.select();
        const text = input.value;
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                if (toast) {
                    toast.classList.remove('hidden');
                    setTimeout(() => toast.classList.add('hidden'), 3000);
                }
            }).catch(() => {
                document.execCommand('copy');
                if (toast) {
                    toast.classList.remove('hidden');
                    setTimeout(() => toast.classList.add('hidden'), 3000);
                }
            });
        } else {
            document.execCommand('copy');
            if (toast) {
                toast.classList.remove('hidden');
                setTimeout(() => toast.classList.add('hidden'), 3000);
            }
        }
    }

    shareViaWhatsApp() {
        if (!this.currentTask || !this.currentRoadmap) return;
        const t = this.currentTask;
        const r = this.currentRoadmap;
        const shareUrl = `${window.location.origin}/?task=${this.currentTaskId}`;

        const stepsText = t.steps.map((s, idx) => `• Step ${idx + 1}: ${s.title} (${s.department.name.split('(')[0].trim()})`).join('\n');

        const message = `🏛️ *Civic Task Navigator — Maharashtra*\n\n*${t.title}*\n📍 Jurisdiction: ${t.municipality}\n⏱️ Timeline: ~${r.total_estimated_days} Working Days\n💰 Official Fees: ₹${r.total_estimated_fees}\n\n📋 *Ordered Procedure Steps:*\n${stepsText}\n\n🔗 *Explore interactive roadmap & required documents:*\n${shareUrl}`;

        window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(message)}`, '_blank');
    }

    // -------------------------------------------------------------------------
    // Application Status Tracker Engine
    // -------------------------------------------------------------------------
    trackApplicationStatus() {
        const tokenInput = document.getElementById('input-track-token');
        const portalSelect = document.getElementById('select-track-portal');
        const token = tokenInput ? tokenInput.value.trim() : '';
        const portal = portalSelect ? portalSelect.value : 'aaple_sarkar';

        let targetUrl = 'https://aaplesarkar.mahaonline.gov.in/en/TrackApplicationStatus';
        if (portal === 'mcgm') {
            targetUrl = 'https://portal.mcgm.gov.in';
        } else if (portal === 'mahabhumi') {
            targetUrl = 'https://bhulekh.mahabhumi.gov.in';
        } else if (portal === 'foscos') {
            targetUrl = 'https://foscos.fssai.gov.in';
        }

        if (token) {
            alert(`Opening official tracking gateway for Token #${token}...`);
        }
        window.open(targetUrl, '_blank');
    }

    switchNavTab(tabName) {
        this.activeTab = tabName;
        window.location.hash = tabName;

        // Update nav buttons
        document.querySelectorAll('#top-nav-tabs .nav-tab-btn').forEach(btn => {
            const matches = btn.getAttribute('data-path') === tabName;
            btn.classList.toggle('active', matches);
        });

        // Hide/Show tab panes
        const panes = ['task-lookup', 'roadmap-and-route', 'step-dossier', 'document-locker', 'citizen-ledger', 'registry-admin'];
        panes.forEach(pane => {
            const el = document.getElementById(`view-${pane}`);
            if (el) {
                el.style.display = (pane === tabName) ? 'flex' : 'none';
            }
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });

        if (tabName === 'roadmap-and-route') {
            if (this.wayfindingMode === 'dag') {
                setTimeout(() => this.visualizer.fitToScreen(), 50);
            }
        } else if (tabName === 'document-locker') {
            this.renderDocumentLocker();
        } else if (tabName === 'citizen-ledger') {
            this.renderCitizenLedger();
        } else if (tabName === 'registry-admin') {
            if (this.admin) this.admin.switchTab('scraper');
        }
    }

    // -------------------------------------------------------------------------
    // Tasks Catalog & Dynamic Jurisdiction Intake
    // -------------------------------------------------------------------------
    async loadTasksList() {
        try {
            const resp = await fetch('/api/tasks');
            if (resp.ok) {
                this.allTasks = await resp.json();
                this.renderTasksCatalog();
                this.populateJurisdictionDropdowns();
            }
        } catch (e) {
            console.error('Failed to load tasks list', e);
        }
    }

    renderTasksCatalog() {
        const container = document.getElementById('directives-ledger-list');
        if (!container || !this.allTasks || this.allTasks.length === 0) return;

        const isMr = (this.currentLang === 'mr');

        container.innerHTML = this.allTasks.map((t, idx) => {
            const isActive = t.id === this.currentTaskId;
            const stepCount = (t.steps && t.steps.length) || 0;
            const daysEst = isMr 
                ? `${t.total_estimated_days || 15}–${(t.total_estimated_days || 15) + 10} दिवस` 
                : `${t.total_estimated_days || 15}–${(t.total_estimated_days || 15) + 10} Days`;
            const feesEst = this.formatINR(t.total_fees || 0);
            const indexStr = idx < 9 ? `0${idx + 1}` : `${idx + 1}`;

            const taskTitle = this.getTaskTitle(t);
            const taskDesc = this.getTaskDesc(t);
            const taskMuni = this.getTaskMunicipality(t);

            // Authorities summary
            let authorityTags = taskMuni;
            if (t.steps && t.steps.length > 0) {
                const uniqueDepts = Array.from(new Set(t.steps.map(s => {
                    const deptName = this.getStepDept(s, t.id);
                    return deptName ? deptName.split('(')[0].trim() : '';
                }))).filter(Boolean);
                if (uniqueDepts.length > 0) {
                    authorityTags = uniqueDepts.slice(0, 3).join(' • ');
                }
            }

            const activeBadgeText = isMr ? 'सक्रिय प्रक्रिया' : 'Active Focus';
            const colJurisdiction = isMr ? 'अधिकारक्षेत्र व साखळी' : 'Jurisdiction & Chain';
            const colSchedule = isMr ? 'अंदाजे कालावधी' : 'Est. Schedule';
            const colFees = isMr ? 'अधिकृत शुल्क' : 'Total Fees';
            const btnLoad = isMr ? 'मार्ग पहा' : 'Load Route';

            return `
                <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 ${isActive ? 'bg-amber-50/50 border-l-4 border-amber-600' : ''}" onclick="window.app.loadTaskAndRoute('${t.id}')">
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 ${isActive ? 'bg-amber-700 text-white' : 'bg-primary text-on-primary'} flex items-center justify-center font-code text-xs font-bold border border-primary shrink-0">
                            ${indexStr}
                        </div>
                        <div>
                            <div class="font-headline text-sm font-semibold text-primary flex items-center gap-2 flex-wrap">
                                <span>${taskTitle}</span>
                                ${isActive ? `<span class="bg-amber-100 text-amber-900 font-label-sm text-[10px] px-1.5 py-0.5 font-bold uppercase border border-amber-300">${activeBadgeText}</span>` : ''}
                                <span class="bg-surface-container text-secondary font-code text-[10px] px-1.5 py-0.5 border border-outline-variant">${taskMuni}</span>
                            </div>
                            <div class="font-body text-xs text-on-surface-variant mt-0.5 max-w-2xl line-clamp-2">
                                ${taskDesc}
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center gap-6 shrink-0 text-xs font-headline">
                        <div class="text-right hidden sm:block">
                            <div class="text-secondary text-[11px] uppercase">${colJurisdiction}</div>
                            <div class="font-code text-primary font-semibold truncate max-w-[180px]">${authorityTags}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-secondary text-[11px] uppercase">${colSchedule}</div>
                            <div class="font-code text-primary font-semibold">${daysEst}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-secondary text-[11px] uppercase">${colFees}</div>
                            <div class="font-code text-primary font-bold">${feesEst}</div>
                        </div>
                        <button class="${isActive ? 'bg-amber-700 text-white' : 'bg-surface-container text-primary hover:bg-primary hover:text-on-primary'} px-3 py-1.5 text-xs font-semibold transition-colors border border-outline-variant shrink-0" onclick="event.stopPropagation(); window.app.loadTaskAndRoute('${t.id}')">
                            ${btnLoad}
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    populateJurisdictionDropdowns() {
        if (!this.allTasks || this.allTasks.length === 0) return;

        const isMr = (this.currentLang === 'mr');
        // Extract unique municipalities
        const uniqueMunis = Array.from(new Set(this.allTasks.map(t => t.municipality))).filter(Boolean);

        // 1. Top Navbar Jurisdiction Dropdown
        const navSelect = document.getElementById('select-jurisdiction');
        if (navSelect) {
            navSelect.innerHTML = uniqueMunis.map(m => {
                const label = isMr ? (window.MUNI_TRANSLATIONS?.[m] || m) : m;
                return `<option value="${m}" ${this.currentTask && this.currentTask.municipality === m ? 'selected' : ''}>${label}</option>`;
            }).join('');

            // Clean event listener
            navSelect.onchange = (e) => {
                const selectedMuni = e.target.value;
                const matchTask = this.allTasks.find(t => t.municipality === selectedMuni);
                if (matchTask) {
                    this.loadTaskAndRoute(matchTask.id);
                }
            };
        }

        // 2. Search Intake Jurisdiction Dropdown
        const searchSelect = document.getElementById('jurisdictionSelect');
        if (searchSelect) {
            const allLabel = isMr ? 'सर्व महानगरपालिका / अधिकारक्षेत्र (महाराष्ट्र)' : 'All Municipal Jurisdictions (National)';
            searchSelect.innerHTML = `
                <option value="">${allLabel}</option>
                ${uniqueMunis.map(m => {
                    const label = isMr ? (window.MUNI_TRANSLATIONS?.[m] || m) : m;
                    return `<option value="${m}">${label}</option>`;
                }).join('')}
            `;
        }
    }

    // -------------------------------------------------------------------------
    // Task Route Loading & DAG Formulation
    // -------------------------------------------------------------------------
    async loadTaskAndRoute(taskId) {
        // 1. Load scoped persistence
        this.loadTaskScopedState(taskId);

        // 2. Load roadmap from server
        await this.loadRoadmap(taskId);

        // 3. Update task catalog highlight & dropdowns
        this.renderTasksCatalog();
        const navSelect = document.getElementById('select-jurisdiction');
        if (navSelect && this.currentTask) {
            navSelect.value = this.currentTask.municipality;
        }

        // 4. Default station selection
        if (this.currentTask && this.currentTask.steps.length > 0) {
            const firstPending = this.currentTask.steps.find(s => !this.completedStepIds.has(s.id));
            const targetStepId = firstPending ? firstPending.id : this.currentTask.steps[0].id;
            this.selectStation(targetStepId);
        }

        // 5. Navigate to roadmap view
        this.switchNavTab('roadmap-and-route');
    }

    async loadRoadmap(taskId) {
        try {
            const resp = await fetch(`/api/tasks/${taskId}/roadmap`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    completed_step_ids: Array.from(this.completedStepIds),
                    in_progress_step_ids: Array.from(this.inProgressStepIds)
                })
            });

            if (!resp.ok) throw new Error('Failed to load roadmap');
            this.currentRoadmap = await resp.json();
            this.currentTask = this.currentRoadmap.task;

            // Auto-initialize root steps as ready/in-progress if brand new task
            if (this.completedStepIds.size === 0 && this.inProgressStepIds.size === 0 && this.currentTask.steps.length > 0) {
                const rootSteps = this.currentTask.steps.filter(s => !s.prerequisites || s.prerequisites.length === 0);
                rootSteps.forEach(rs => this.inProgressStepIds.add(rs.id));
                this.saveTaskInProgress();
            }

            // Sync visual components
            this.updateHeaderAndStats();
            this.visualizer.setRoadmapData(this.currentRoadmap);
            this.renderRailMilestones();
            this.updateStationUI();
            this.renderCitizenLedger();

            // Render Dynamic Subway Transit SVG
            if (this.subwayRenderer) {
                this.subwayRenderer.render(
                    this.currentTask,
                    this.currentRoadmap,
                    this.completedStepIds,
                    this.selectedStationId
                );
            }

            if (this.activeTab === 'document-locker') {
                this.renderDocumentLocker();
            }
        } catch (e) {
            console.error('Roadmap error', e);
        }
    }

    updateHeaderAndStats() {
        const t = this.currentTask;
        const r = this.currentRoadmap;
        if (!t || !r) return;

        const isMr = (this.currentLang === 'mr');
        const taskTitle = this.getTaskTitle(t);
        const taskDesc = this.getTaskDesc(t);
        const taskMuni = this.getTaskMunicipality(t);
        const taskCat = this.getTaskCategory(t);

        // Roadmap title & description
        const elTitle = document.getElementById('roadmap-heading-title');
        const elDesc = document.getElementById('roadmap-heading-desc');
        const elRouteId = document.getElementById('route-id-badge');
        const elRouteClass = document.getElementById('route-class-badge');

        if (elTitle) elTitle.innerText = isMr ? `प्रक्रिया मार्ग: ${taskTitle}` : `Route Map: ${t.title}`;
        if (elDesc) elDesc.innerText = taskDesc;
        if (elRouteId) elRouteId.innerText = isMr ? `मार्ग #${t.id.toUpperCase().replace('TASK-', '')}` : `ROUTE #${t.id.toUpperCase().replace('TASK-', '')}`;
        if (elRouteClass) elRouteClass.innerText = taskCat;

        // Dynamic Inter-Agency Code under subway map
        const elInterCode = document.getElementById('subway-interagency-code');
        if (elInterCode) {
            const muniCode = (t.municipality || 'MUNI').split(' ')[0].toUpperCase();
            const catCode = (t.category || 'STATUTORY').toUpperCase().replace(/[^A-Z]/g, '-').slice(0, 10);
            elInterCode.innerText = isMr ? `आंतर-विभाग सांकेतांक: ${catCode}-${muniCode}-2026` : `INTER-AGENCY CODE: ${catCode}-${muniCode}-2026`;
        }

        // Summary stats ribbon
        const elTimeline = document.getElementById('summary-stat-timeline');
        const elFees = document.getElementById('summary-stat-fees');
        const elProgress = document.getElementById('summary-stat-progress');
        const elBlocker = document.getElementById('summary-stat-blocker');
        const elAntiToutFee = document.getElementById('anti-tout-total-fee');
        const elDocs = document.getElementById('summary-stat-docs');

        const totalSteps = t.steps ? t.steps.length : 0;
        const doneSteps = this.completedStepIds.size;

        if (elTimeline) elTimeline.innerText = `${r.total_estimated_days}–${r.total_estimated_days + 15}`;
        if (elFees) elFees.innerText = this.formatINR(r.total_estimated_fees || 0);
        if (elAntiToutFee) elAntiToutFee.innerText = this.formatINR(r.total_estimated_fees || 0);
        if (elProgress) elProgress.innerText = `${doneSteps} / ${totalSteps}`;

        if (elDocs && r.consolidated_documents) {
            const totalDocs = r.consolidated_documents.length;
            const readyDocs = r.consolidated_documents.filter(d => this.checkedDocIds.has(d.name)).length;
            elDocs.innerText = `${readyDocs} / ${totalDocs}`;
        }

        if (elBlocker) {
            const firstPending = t.steps.find(s => !this.completedStepIds.has(s.id));
            if (firstPending) {
                const deptName = this.getStepDept(firstPending, t.id);
                elBlocker.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500 shrink-0"></span> ${deptName.split('(')[0]}`;
            } else {
                elBlocker.innerHTML = isMr
                    ? `<span class="w-2 h-2 rounded-full bg-emerald-600 shrink-0"></span> सर्व टप्पे यशस्वीरित्या पूर्ण`
                    : `<span class="w-2 h-2 rounded-full bg-emerald-600 shrink-0"></span> All Milestones Cleared`;
            }
        }

        // NLP Intent Resolution & Provenance Banner
        const elNlpBanner = document.getElementById('nlp-intent-banner');
        if (elNlpBanner) {
            if (this.lastSearchNotice) {
                elNlpBanner.classList.remove('hidden');
                elNlpBanner.style.display = 'flex';
                const isSynth = this.lastSearchNotice.type === 'synthesized';
                elNlpBanner.className = isSynth
                    ? 'mb-4 p-3 bg-purple-50 border border-purple-300 text-purple-950 font-headline text-xs flex items-center justify-between gap-3 shadow-sm'
                    : 'mb-4 p-3 bg-blue-50 border border-blue-300 text-blue-950 font-headline text-xs flex items-center justify-between gap-3 shadow-sm';
                const icon = isSynth ? 'auto_awesome' : 'translate';
                const dismissLabel = isMr ? 'बंद करा' : 'Dismiss';
                elNlpBanner.innerHTML = `
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-[18px] ${isSynth ? 'text-purple-700' : 'text-blue-700'}">${icon}</span>
                        <span>${this.lastSearchNotice.message}</span>
                    </div>
                    <button class="text-secondary hover:text-primary underline text-[11px]" onclick="document.getElementById('nlp-intent-banner').style.display='none'">${dismissLabel}</button>
                `;
            } else {
                elNlpBanner.classList.add('hidden');
                elNlpBanner.style.display = 'none';
            }
        }
    }

    renderRailMilestones() {
        const container = document.getElementById('rail-stations-list');
        const countBadge = document.getElementById('rail-milestones-count');
        if (!container || !this.currentTask) return;

        const isMr = (this.currentLang === 'mr');
        const steps = this.currentTask.steps;
        if (countBadge) countBadge.innerText = isMr ? `${steps.length} टप्पे` : `${steps.length} Stops`;

        container.innerHTML = steps.map((s, idx) => {
            const isCompleted = this.completedStepIds.has(s.id);
            const isSelected = this.selectedStationId === s.id;
            const stepTitle = this.getStepTitle(s, this.currentTask.id);
            const deptName = this.getStepDept(s, this.currentTask.id);
            
            let statusBadge = isMr ? '<span class="font-headline text-[10px] text-secondary">प्रलंबित</span>' : '<span class="font-headline text-[10px] text-secondary">Upcoming</span>';
            let dotBg = 'bg-surface-container-highest text-secondary';
            if (isCompleted) {
                statusBadge = isMr ? '<span class="font-headline text-[10px] text-emerald-800 font-bold">✓ पूर्ण</span>' : '<span class="font-headline text-[10px] text-emerald-800 font-bold">✓ Cleared</span>';
                dotBg = 'bg-emerald-700 text-white';
            } else if (isSelected) {
                statusBadge = isMr ? '<span class="font-headline text-[10px] text-amber-800 font-bold">सक्रिय</span>' : '<span class="font-headline text-[10px] text-amber-800 font-bold">Active</span>';
                dotBg = 'bg-amber-500 text-white';
            }

            return `
                <div class="p-2 border border-outline-variant flex items-center justify-between cursor-pointer hover:bg-surface-container-low transition-colors ${isSelected ? 'bg-surface-container-low border-l-4 border-l-amber-500' : 'bg-surface-container-lowest'}" onclick="window.app.selectStation('${s.id}')">
                    <div class="flex items-center gap-2">
                        <span class="w-5 h-5 rounded-full ${dotBg} flex items-center justify-center font-code text-[10px] font-bold">${idx + 1}</span>
                        <div class="truncate max-w-[140px]">
                            <div class="font-headline text-xs font-semibold text-primary truncate">${stepTitle}</div>
                            <div class="font-code text-[10px] text-secondary truncate">${deptName.split('(')[0]}</div>
                        </div>
                    </div>
                    <div>${statusBadge}</div>
                </div>
            `;
        }).join('');
    }

    selectStation(stepId) {
        this.selectedStationId = stepId;
        this.updateStationUI();
        this.renderRailMilestones();

        // Refresh Subway Map Highlight
        if (this.subwayRenderer && this.currentTask && this.currentRoadmap) {
            this.subwayRenderer.render(
                this.currentTask,
                this.currentRoadmap,
                this.completedStepIds,
                this.selectedStationId
            );
        }
    }

    updateStationUI() {
        if (!this.currentTask) return;
        const step = this.currentTask.steps.find(s => s.id === this.selectedStationId) || this.currentTask.steps[0];
        if (!step) return;

        const isMr = (this.currentLang === 'mr');
        const isCompleted = this.completedStepIds.has(step.id);
        const stateCode = (this.currentTask.state || this.currentTask.municipality || 'IN').substring(0, 2).toUpperCase();
        const stepTitle = this.getStepTitle(step, this.currentTask.id);
        const stepDesc = this.getStepDesc(step, this.currentTask.id);
        const deptName = this.getStepDept(step, this.currentTask.id);
        const muniName = this.getTaskMunicipality(this.currentTask);

        // 1. Update Active Station Dossier Card on Roadmap view
        const badgeStep = document.getElementById('station-badge-step');
        const badgeStatus = document.getElementById('station-badge-status');
        const badgeAgency = document.getElementById('station-badge-agency');
        const titleEl = document.getElementById('station-title');
        const descEl = document.getElementById('station-desc');
        const slaEl = document.getElementById('station-sla-days');
        const feeEl = document.getElementById('station-fee-amount');
        const checklistEl = document.getElementById('station-checklist');
        const docketRef = document.getElementById('station-docket-ref');

        if (badgeStep) badgeStep.innerText = isMr 
            ? `टप्पा 0${step.step_number} / ${muniName}`
            : `STOP 0${step.step_number} / ${(step.department.jurisdiction || this.currentTask.municipality).toUpperCase()}`;
        if (badgeAgency) badgeAgency.innerText = isMr ? `विभाग: ${deptName}` : `Agency: ${step.department.name}`;
        if (titleEl) titleEl.innerText = stepTitle;
        if (descEl) descEl.innerText = stepDesc;
        if (slaEl) slaEl.innerText = isMr ? `${step.estimated_days} दिवस` : `${step.estimated_days} Days`;
        if (feeEl) feeEl.innerText = step.fee_amount > 0 ? this.formatINR(step.fee_amount) : (isMr ? 'विनामूल्य' : 'Exempt');
        if (docketRef) docketRef.innerText = isMr ? `डॉकेट संदर्भ: ${stateCode}-${step.id.toUpperCase()}-2026` : `DOCKET REF: ${stateCode}-${step.id.toUpperCase()}-2026`;

        if (badgeStatus) {
            if (isCompleted) {
                badgeStatus.className = 'bg-emerald-100 text-emerald-900 font-headline text-xs px-2.5 py-0.5 font-bold uppercase flex items-center gap-1';
                badgeStatus.innerHTML = isMr
                    ? '<span class="material-symbols-outlined text-[14px]">done_all</span> पूर्ण व प्रमाणित'
                    : '<span class="material-symbols-outlined text-[14px]">done_all</span> Satisfied &amp; Verified';
            } else {
                badgeStatus.className = 'bg-amber-100 text-amber-900 font-headline text-xs px-2.5 py-0.5 font-bold uppercase flex items-center gap-1';
                badgeStatus.innerHTML = isMr
                    ? '<span class="w-2 h-2 rounded-full bg-amber-600 animate-ping"></span> प्रक्रियेत'
                    : '<span class="w-2 h-2 rounded-full bg-amber-600 animate-ping"></span> In Progress';
            }
        }

        if (checklistEl) {
            checklistEl.innerHTML = step.documents.map(d => {
                const docLabel = this.getDocName(d.name);
                const reqLabel = d.is_mandatory ? (isMr ? 'अनिवार्य' : 'Mandatory') : (isMr ? 'पर्यायी' : 'Optional');
                return `
                <label class="flex items-start gap-1.5 font-body text-xs text-on-surface cursor-pointer">
                    <span class="material-symbols-outlined ${isCompleted ? 'text-emerald-700' : 'text-amber-600'} text-[18px]">${isCompleted ? 'check_box' : 'indeterminate_check_box'}</span>
                    <span>${docLabel} (${reqLabel})</span>
                </label>
            `;
            }).join('') || `<div class="text-xs text-secondary font-headline">${isMr ? 'या टप्प्यासाठी पूर्व कागदपत्रे आवश्यक नाहीत.' : 'No prior physical filings required for this station.'}</div>`;
        }

        // Pre-fill Citizen Application / Challan Input with saved data
        const appInput = document.getElementById('statutory-app-num') || document.getElementById('mcgm-app-num');
        if (appInput) {
            appInput.value = this.stepApplicationNumbers[step.id] || '';
        }
        const chkSelf = document.getElementById('chk-self-declaration');
        if (chkSelf) chkSelf.checked = false;

        // 2. Update Step Dossier Tab View
        this.populateDossierView(step);

        // 3. Update Drawer content
        this.populateDrawer(step);

        // 4. Update Dynamic Roadmap Steps List
        this.renderRoadmapStepCards();
    }

    renderRoadmapStepCards() {
        const container = document.getElementById('roadmap-steps-container');
        if (!container || !this.currentTask) return;

        const isMr = (this.currentLang === 'mr');

        container.innerHTML = this.currentTask.steps.map((s, idx) => {
            const isCompleted = this.completedStepIds.has(s.id);
            const isSelected = this.selectedStationId === s.id;
            const prereqs = s.prerequisites || [];
            const prereqsMet = prereqs.every(pId => this.completedStepIds.has(pId));
            const stepTitle = this.getStepTitle(s, this.currentTask.id);
            const stepDesc = this.getStepDesc(s, this.currentTask.id);
            const deptName = this.getStepDept(s, this.currentTask.id);

            let statusBadge = '';
            let dotBg = '';
            if (isCompleted) {
                statusBadge = isMr
                    ? '<span class="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-1 rounded-full font-semibold flex items-center gap-1">✓ पूर्ण</span>'
                    : '<span class="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-1 rounded-full font-semibold flex items-center gap-1">✓ Completed</span>';
                dotBg = 'bg-emerald-700 text-white';
            } else if (!prereqsMet) {
                statusBadge = isMr
                    ? '<span class="bg-slate-100 text-slate-600 text-xs px-2.5 py-1 rounded-full font-medium">मागील टप्प्यांची प्रतीक्षा</span>'
                    : '<span class="bg-slate-100 text-slate-600 text-xs px-2.5 py-1 rounded-full font-medium">Waiting on Prerequisite</span>';
                dotBg = 'bg-slate-300 text-slate-700';
            } else if (isSelected) {
                statusBadge = isMr
                    ? '<span class="bg-amber-100 text-amber-900 text-xs px-2.5 py-1 rounded-full font-semibold">● अर्ज करण्यास सज्ज</span>'
                    : '<span class="bg-amber-100 text-amber-900 text-xs px-2.5 py-1 rounded-full font-semibold">● Ready to Apply</span>';
                dotBg = 'bg-amber-500 text-white';
            } else {
                statusBadge = isMr
                    ? '<span class="bg-blue-50 text-blue-800 text-xs px-2.5 py-1 rounded-full font-semibold border border-blue-200">सुरू करण्यास सज्ज</span>'
                    : '<span class="bg-blue-50 text-blue-800 text-xs px-2.5 py-1 rounded-full font-semibold border border-blue-200">Ready to Start</span>';
                dotBg = 'bg-primary text-white';
            }

            const feeText = s.fee_amount > 0 ? this.formatINR(s.fee_amount) : (isMr ? 'विनामूल्य / शून्य शुल्क' : 'Free / Nil');
            const slaText = isMr ? `${s.estimated_days} दिवस (SLA)` : `${s.estimated_days} Days SLA`;
            const docText = isMr ? `${(s.documents || []).length} कागदपत्रे` : `${(s.documents || []).length} Documents`;
            const criticalPathText = isMr ? '⚡ महत्त्वाचा मार्ग' : '⚡ Critical Path';
            const btnDetailsText = isMr ? 'तपशील व अर्ज' : 'View Details & Apply';
            const btnDoneText = isCompleted ? (isMr ? 'पूर्ण झाले' : 'Completed') : (isMr ? 'झाले म्हणून खूण करा' : 'Mark Done');

            return `
                <div class="bg-surface-container-lowest border ${isSelected ? 'border-amber-500 ring-2 ring-amber-400/20' : 'border-outline-variant'} rounded-md p-5 shadow-sm hover:shadow transition-all" id="step-card-${s.id}">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-outline-variant/30">
                        <div class="flex items-center gap-3">
                            <span class="w-8 h-8 rounded-full ${dotBg} flex items-center justify-center font-code text-xs font-bold shrink-0">
                                ${isCompleted ? '✓' : idx + 1}
                            </span>
                            <div>
                                <h3 class="font-headline text-base font-semibold text-primary cursor-pointer hover:text-amber-800" onclick="window.app.selectStation('${s.id}')">${stepTitle}</h3>
                                <p class="font-headline text-xs text-secondary">${deptName} • ${s.department.jurisdiction || this.currentTask.municipality}</p>
                            </div>
                        </div>
                        <div class="self-start sm:self-auto">${statusBadge}</div>
                    </div>

                    <p class="font-body text-xs text-on-surface-variant mt-3 leading-relaxed">${stepDesc}</p>

                    <div class="mt-4 pt-3 border-t border-outline-variant/30 flex flex-wrap items-center justify-between gap-3 text-xs">
                        <div class="flex items-center gap-4 text-secondary font-headline">
                            <span>⏱️ <strong>${slaText}</strong></span>
                            <span>💰 <strong>${feeText}</strong></span>
                            <span>📄 <strong>${docText}</strong></span>
                            ${s.is_critical_path ? `<span class="text-amber-700 font-semibold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">${criticalPathText}</span>` : ''}
                        </div>

                        <div class="flex items-center gap-2">
                            <button onclick="window.app.selectStation('${s.id}'); window.app.switchNavTab('step-dossier');" class="bg-surface-container hover:bg-surface-container-high text-primary font-headline text-xs font-semibold px-3 py-1.5 rounded transition-colors flex items-center gap-1 border border-outline-variant">
                                <span>${btnDetailsText}</span>
                                <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
                            </button>
                            <button onclick="window.app.toggleStepComplete('${s.id}')" class="${isCompleted ? 'bg-emerald-700 hover:bg-emerald-800 text-white' : 'bg-primary hover:bg-primary-container text-white'} font-headline text-xs font-semibold px-3 py-1.5 rounded transition-colors flex items-center gap-1 shadow-xs">
                                <span class="material-symbols-outlined text-[14px]">${isCompleted ? 'check' : 'check_circle'}</span>
                                <span>${btnDoneText}</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // -------------------------------------------------------------------------
    // Step Dossier Decoupling: Fully Data-Driven from Task & Step
    // -------------------------------------------------------------------------
    populateDossierView(step) {
        const isCompleted = this.completedStepIds.has(step.id);
        const task = this.currentTask;
        const isMr = (this.currentLang === 'mr');
        const muniCode = (task.municipality || 'IN').split(' ')[0].toUpperCase();
        const stepTitle = this.getStepTitle(step, task.id);
        const stepDesc = this.getStepDesc(step, task.id);
        const deptName = this.getStepDept(step, task.id);
        const muniName = this.getTaskMunicipality(task);
        const taskTitle = this.getTaskTitle(task);
        const taskCat = this.getTaskCategory(task);

        const routeCrumb = document.getElementById('dossier-route-crumb');
        const stepCrumb = document.getElementById('dossier-step-crumb');
        const refCode = document.getElementById('dossier-ref-code');
        const stageIdx = document.getElementById('dossier-stage-idx');
        const agencyName = document.getElementById('dossier-agency-name');
        const mainTitle = document.getElementById('dossier-main-title');
        const mainDesc = document.getElementById('dossier-main-desc');
        const statusText = document.getElementById('dossier-status-text');
        const statusDot = document.getElementById('dossier-status-dot');
        const statusSla = document.getElementById('dossier-status-sla');
        const provText = document.getElementById('dossier-provenance-text');
        const provLink = document.getElementById('dossier-provenance-link');
        const provLinkText = document.getElementById('dossier-provenance-link-text');

        if (routeCrumb) routeCrumb.innerText = taskTitle;
        if (stepCrumb) stepCrumb.innerText = isMr ? `टप्पा 0${step.step_number} (${stepTitle})` : `Stop 0${step.step_number} (${step.title})`;
        if (refCode) refCode.innerText = isMr ? `नोंद संदर्भ: ${muniCode}-${step.id.toUpperCase()}-2026` : `REF: ${muniCode}-${step.id.toUpperCase()}-2026`;
        if (stageIdx) stageIdx.innerText = isMr ? `टप्पा 0${step.step_number} / 0${task.steps.length}` : `STAGE 0${step.step_number} / 0${task.steps.length}`;
        if (agencyName) agencyName.innerText = `${deptName} (${muniName})`;
        if (mainTitle) mainTitle.innerText = isMr ? `टप्पा 0${step.step_number}: ${stepTitle}` : `Step 0${step.step_number}: ${step.title}`;
        if (mainDesc) mainDesc.innerText = stepDesc;

        if (statusText) statusText.innerText = isCompleted 
            ? (isMr ? 'प्रमाणित व दप्तरी नोंदणीकृत ✓' : 'Cleared & Verified on File') 
            : (isMr ? 'प्रक्रियेत: कार्यवाही आवश्यक' : 'In Progress: Action Required');
        if (statusDot) statusDot.className = isCompleted ? 'w-2.5 h-2.5 rounded-full bg-emerald-600' : 'w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse';
        if (statusSla) statusSla.innerText = isMr ? `नियत सेवा हमी कालावधी (RTS): ${step.estimated_days} कामकाजाचे दिवस` : `Target Statutory Window: ${step.estimated_days} Working Days`;

        // Verification Freshness Sentinel & Crowd Confirmation
        const gazetteTag = document.getElementById('dossier-gazette-tag');
        const verifiedDate = document.getElementById('dossier-verified-date');
        const crowdCount = document.getElementById('dossier-crowd-count');
        const statutoryAuth = step.last_gazette_notification || (step.verification_source && step.verification_source.gazette_ref) || (isMr ? `${taskCat} वैधानिक नियमावली` : `${task.category} Statutory Regulations`);

        if (gazetteTag) gazetteTag.innerText = statutoryAuth;
        if (verifiedDate) verifiedDate.innerText = this.formatDateIN(step.verification_source ? step.verification_source.last_scraped_at : null);
        if (crowdCount) crowdCount.innerText = isMr 
            ? `या महिन्यात ${muniName} मध्ये ${step.community_verifications || 14} नागरिकांनी हा टप्पा यशस्वीरित्या पूर्ण केला` 
            : `${step.community_verifications || 14} citizens successfully processed this milestone across ${task.municipality} this month`;

        if (provText) {
            provText.innerHTML = isMr
                ? `<strong>${statutoryAuth}</strong> आणि <strong>${this.formatDateIN(step.verification_source?.last_scraped_at)}</strong> नुसार अधिकृतपणे प्रमाणित.`
                : `Verified against <strong>${statutoryAuth}</strong> as of <strong>${this.formatDateIN(step.verification_source?.last_scraped_at)}</strong>.`;
        }
        if (provLink && provLinkText && step.verification_source) {
            provLink.href = step.verification_source.url || '#';
            provLinkText.innerText = (step.verification_source.url || 'portal.gov.in').replace('https://', '').replace('http://', '');
        }

        // Anti-Tout Sovereign Payment Notice
        const paymentChan = document.getElementById('dossier-payment-channel');
        const antiToutText = document.getElementById('dossier-anti-tout-text');
        const receiptMandate = document.getElementById('dossier-receipt-mandate');
        
        const defaultChannel = isMr ? `${deptName} अधिकृत शासकीय ई-चलन / राजकोष (Gras MahaKosh)` : `${step.department.name} Official Treasury E-Challan / Bharatkosh`;
        const defaultAdvisory = isMr 
            ? `अधिकृत सूचना: कोणत्याही दलालाला रोख रक्कम देऊ नका. ${deptName} चे सर्व शासकीय शुल्क अधिकृत शासकीय ई-पावती / जीआरएन (GRN) द्वारेच जमा करावे.`
            : step.anti_tout_advisory || `Official Advisory: Never pay cash to middlemen. All statutory fees for ${step.department.name} must be deposited via verified Government E-Receipt / GRN.`;
        const defaultReceipt = isMr 
            ? 'रोख व्यवहार बंदी: संगणकीकृत शासकीय ई-पावती अनिवार्य.' 
            : (step.official_receipt_mandate || 'Zero Cash Mandate: Computerized Government Treasury E-Receipt required.');

        if (paymentChan) paymentChan.innerText = step.statutory_payment_channel || defaultChannel;
        if (antiToutText) antiToutText.innerText = defaultAdvisory;
        if (receiptMandate) receiptMandate.innerText = defaultReceipt;

        // Prerequisites bar
        const prereqGrid = document.getElementById('dossier-prereqs-grid');
        const prereqStatus = document.getElementById('dossier-prereq-chain-status');
        if (prereqGrid) {
            if (!step.prerequisites || step.prerequisites.length === 0) {
                prereqGrid.innerHTML = `
                    <div class="col-span-2 bg-surface-container-lowest p-3 border border-outline-variant text-xs text-secondary font-headline">
                        ${isMr ? `✓ प्रारंभिक टप्पा: ${muniName} च्या वैधानिक नियमांनुसार थेट अर्ज करता येणारा टप्पा.` : `✓ Station Initializer: Root procedural milestone under ${task.municipality} statutory rules.`}
                    </div>
                `;
                if (prereqStatus) prereqStatus.innerText = isMr ? 'साखळी स्थिती: प्रारंभिक टप्पा' : 'CHAIN STATUS: ROOT MILESTONE';
            } else {
                const totalReq = step.prerequisites.length;
                const clearedReq = step.prerequisites.filter(p => this.completedStepIds.has(p)).length;
                if (prereqStatus) prereqStatus.innerText = isMr ? `साखळी स्थिती: ${clearedReq}/${totalReq} पूर्ण` : `CHAIN STATUS: ${clearedReq}/${totalReq} SATISFIED`;

                prereqGrid.innerHTML = step.prerequisites.map(pId => {
                    const prereqStep = task.steps.find(s => s.id === pId);
                    const isPrereqDone = this.completedStepIds.has(pId);
                    const pTitle = prereqStep ? this.getStepTitle(prereqStep, task.id) : pId;
                    const badgeLabel = isMr ? (isPrereqDone ? 'पूर्ण' : 'प्रलंबित') : (isPrereqDone ? 'Cleared' : 'Pending');
                    const subLabel = isMr ? 'मागील टप्पा पूर्तता' : 'Prerequisite Clearance';
                    return `
                        <div class="bg-surface-container-lowest p-3 border border-outline-variant flex items-center justify-between">
                            <div class="flex items-center gap-2.5">
                                <span class="w-5 h-5 rounded-full ${isPrereqDone ? 'bg-emerald-800 text-white' : 'bg-surface-container text-secondary'} flex items-center justify-center font-code text-[11px] font-bold">
                                    ${isPrereqDone ? '✓' : '•'}
                                </span>
                                <div>
                                    <div class="font-headline text-xs font-semibold text-primary">${pTitle}</div>
                                    <div class="font-code text-[10px] text-secondary">${subLabel}</div>
                                </div>
                            </div>
                            <span class="font-headline text-[10px] ${isPrereqDone ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-amber-50 text-amber-900 border border-amber-300'} px-2 py-0.5 font-semibold">
                                ${badgeLabel}
                            </span>
                        </div>
                    `;
                }).join('');
            }
        }

        // Statutory Forms
        const formsContainer = document.getElementById('dossier-forms-container');
        const formsCount = document.getElementById('dossier-forms-count');
        if (formsContainer) {
            const forms = step.forms || [];
            if (formsCount) formsCount.innerText = isMr ? `${forms.length} विहित नमुने` : `${forms.length} Prescribed Instruments`;
            formsContainer.innerHTML = forms.map(f => `
                <div class="py-3 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div class="space-y-0.5 max-w-xl">
                        <div class="flex items-center gap-2">
                            <span class="font-code text-xs font-semibold bg-surface-container px-2 py-0.5 border border-outline-variant text-primary">${f.form_code}</span>
                            <h3 class="font-headline text-sm font-semibold text-primary">${f.title}</h3>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant leading-relaxed">${isMr ? 'शासकीय व महानगरपालिका नियमांनुसार अर्जासाठी आवश्यक अधिकृत विहित नमुना.' : 'Official administrative instrument required for filing under municipal procedure code.'}</p>
                        <div class="font-code text-[11px] text-secondary">${isMr ? 'अधिकृत स्वरूप: डिजिटल ई-फाइलिंग किंवा पीडीएफ दस्तऐवज' : 'Authorized Format: Digital E-Filing or PDF Document'}</div>
                    </div>
                    <a class="inline-flex items-center justify-center gap-1.5 bg-surface-container-lowest text-primary border border-outline hover:bg-surface-container-low px-4 py-2 font-headline text-xs font-semibold transition-colors shrink-0" href="${f.download_url || f.fill_online_url || '#'}" target="_blank">
                        <span class="material-symbols-outlined text-[16px]">download</span>
                        <span>${isMr ? `अधिकृत नमुना (${f.download_url ? 'PDF डाउनलोड' : 'ई-पोर्टल'})` : `Official Instrument (${f.download_url ? 'PDF' : 'E-Portal'})`}</span>
                    </a>
                </div>
            `).join('') || `<div class="text-xs text-secondary font-headline">${isMr ? 'स्वतंत्र नमुना आवश्यक नाही. थेट स्वयंघोषणापत्रासह अर्ज करा.' : 'No separate form instruments prescribed. Proceed with direct declaration.'}</div>`;
        }

        // Evidence & Required Filings
        const evidenceContainer = document.getElementById('dossier-evidence-container');
        const evidenceCount = document.getElementById('dossier-evidence-count');
        if (evidenceContainer) {
            const docs = step.documents || [];
            if (evidenceCount) evidenceCount.innerText = isMr ? `${docs.length} आवश्यक कागदपत्रे` : `${docs.length} Evidence Criteria`;
            evidenceContainer.innerHTML = docs.map(d => {
                const docName = this.getDocName(d.name);
                return `
                <div class="p-3 bg-surface-container-lowest border border-outline-variant flex flex-col md:flex-row items-start justify-between gap-3">
                    <div class="space-y-0.5 max-w-xl">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-amber-700 text-[18px]">pending</span>
                            <span class="font-headline text-sm font-semibold text-primary">${docName}</span>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant leading-relaxed">${d.description || (isMr ? 'तपासणीसाठी आवश्यक वैधानिक पुरावा.' : 'Statutory proof required by inspection window.')}</p>
                        <div class="font-code text-[11px] text-outline">${isMr ? 'निकष: स्वाक्षरी केलेले व डिजिटल स्वरूपात प्रमाणित असणे आवश्यक' : 'CRITERIA: Must be authenticated and digitally verified'}</div>
                    </div>
                    <div class="shrink-0 flex flex-col items-start md:items-end gap-1">
                        <span class="font-headline text-[10px] bg-amber-50 text-amber-900 border border-amber-300 px-2 py-0.5 font-semibold">${isMr ? (d.is_mandatory ? 'अनिवार्य' : 'ऐच्छिक') : (d.is_mandatory ? 'Mandatory' : 'Optional')}</span>
                        <button class="font-headline text-xs text-primary underline hover:text-secondary font-medium mt-1" onclick="alert('${isMr ? 'कागदपत्र यादी अद्ययावत केली: ' + docName : 'Document checklist updated for: ' + docName}')">${isMr ? 'तयार ठेवा' : 'Upload / Verify'}</button>
                    </div>
                </div>
            `;
            }).join('') || `<div class="text-xs text-secondary font-headline">${isMr ? 'या टप्प्यासाठी अतिरिक्त कागदपत्रांची आवश्यकता नाही.' : 'No additional document filings mandated for this step.'}</div>`;
        }

        // Fee Breakdown Table (in INR ₹)
        const feeTableBody = document.getElementById('dossier-fee-table-body');
        const feeTotalEl = document.getElementById('dossier-fee-total');
        if (feeTableBody) {
            const breakdown = step.fee_breakdown || {};
            const entries = Object.entries(breakdown);
            if (entries.length === 0) {
                feeTableBody.innerHTML = `
                    <tr>
                        <td class="py-2.5 px-4 font-semibold text-primary">${isMr ? 'मानक शासकीय प्रक्रिया शुल्क' : 'Standard Statutory Processing Fee'}</td>
                        <td class="py-2.5 px-4 text-secondary">${isMr ? `${taskCat} शुल्क अनुसूची` : `${task.category} Tariff Schedule`}</td>
                        <td class="py-2.5 px-4 text-right font-code">${isMr ? 'प्रति अर्ज' : 'Per Unit'}</td>
                        <td class="py-2.5 px-4 text-right font-code font-semibold text-primary">${this.formatINR(step.fee_amount)}</td>
                    </tr>
                `;
            } else {
                feeTableBody.innerHTML = entries.map(([key, val]) => `
                    <tr>
                        <td class="py-2.5 px-4 font-semibold text-primary">${key}</td>
                        <td class="py-2.5 px-4 text-secondary">${isMr ? `${taskCat} वैधानिक आधार` : `${task.category} Statutory Basis`}</td>
                        <td class="py-2.5 px-4 text-right font-code">${isMr ? 'अनुसूचीनुसार' : 'Per Filing Schedule'}</td>
                        <td class="py-2.5 px-4 text-right font-code font-semibold text-primary">${this.formatINR(val)}</td>
                    </tr>
                `).join('');
            }
            if (feeTotalEl) feeTotalEl.innerText = this.formatINR(step.fee_amount);
        }

        // Guidelines & Pitfalls
        const guidelinesText = document.getElementById('dossier-guidelines-text');
        if (guidelinesText) {
            guidelinesText.innerText = step.tips_and_pitfalls || (isMr ? `सर्व कागदपत्रे ${muniName} च्या अधिकृत मानकांनुसार आणि वैध नोंदणीनुसार असल्याची खात्री करा.` : `Ensure all submissions conform to ${task.municipality} public service standards and valid registration documents.`);
        }

        // Office Details in Right Rail (Directly Bound from step.department)
        const officeAddress = document.getElementById('dossier-office-address');
        const officeWindow = document.getElementById('dossier-office-window');
        const officeCity = document.getElementById('dossier-office-city');
        const officeHours = document.getElementById('dossier-office-hours');
        const officeBorough = document.getElementById('dossier-office-borough');
        const ombudsPhone = document.getElementById('dossier-ombuds-phone');
        const ombudsEmail = document.getElementById('dossier-ombuds-email');
        const cellTitle = document.getElementById('dossier-cell-title');
        const cellDesc = document.getElementById('dossier-cell-desc');

        const cleanMuni = (task.municipality || 'Civic').toLowerCase().replace(/[^a-z]/g, '');

        if (officeAddress) officeAddress.innerText = step.department.office_address || `${deptName} प्रशासकीय मुख्यालय, ${muniName}`;
        if (officeWindow) officeWindow.innerText = `${deptName} — ${isMr ? 'नागरी सुविधा केंद्र' : 'Civic Facilitation Counter'}`;
        if (officeCity) officeCity.innerText = muniName;
        if (officeHours) officeHours.innerText = isMr ? 'सोमवार ते शुक्रवार: सकाळी १०:०० ते दुपारी ४:००' : (step.department.working_hours || 'Monday – Friday: 10:00 AM – 4:00 PM IST');
        if (officeBorough) officeBorough.innerText = (step.department.jurisdiction || task.municipality).toUpperCase();
        if (ombudsPhone) ombudsPhone.innerText = step.department.contact_phone || '1800-120-8040 (टोल-फ्री)';
        if (ombudsEmail) ombudsEmail.innerText = step.department.contact_email || `support.${cleanMuni}@gov.in`;

        if (cellTitle) cellTitle.innerText = isMr ? `${deptName} नागरिक सहाय्यता कक्ष` : `${step.department.name} Facilitation Desk`;
        if (cellDesc) cellDesc.innerText = isMr ? `${deptName} चे अधिकारी पडताळणी प्रक्रिया आणि कागदपत्रांच्या छाननीमध्ये नागरिकांना सहाय्य करतात.` : `Dedicated administrative officers at ${step.department.name} assist applicants with verification protocols and procedural documentation.`;

        // Action button state
        const advanceBtn = document.getElementById('btn-advance-route');
        const advanceLabel = document.getElementById('btn-advance-label');
        if (advanceBtn && advanceLabel) {
            if (isCompleted) {
                advanceBtn.className = 'w-full bg-emerald-800 text-on-primary px-4 py-3 font-headline text-xs font-semibold tracking-wide border border-emerald-900 transition-colors flex items-center justify-center gap-1.5';
                advanceLabel.innerText = isMr ? 'टप्पा पूर्ण व प्रमाणित झाला ✓' : 'Milestone Cleared & Verified';
            } else {
                advanceBtn.className = 'w-full bg-primary text-on-primary hover:bg-primary-container px-4 py-3 font-headline text-xs font-semibold tracking-wide border border-primary transition-colors flex items-center justify-center gap-1.5';
                advanceLabel.innerText = isMr ? 'टप्पा पूर्ण झाला म्हणून नोंदवा व पुढे चला' : 'Mark Step Complete & Advance';
            }
        }
    }

    populateDrawer(step) {
        const isMr = (this.currentLang === 'mr');
        const stepTitle = this.getStepTitle(step, this.currentTask.id);
        const stepDesc = this.getStepDesc(step, this.currentTask.id);
        const deptName = this.getStepDept(step, this.currentTask.id);
        const muniName = this.getTaskMunicipality(this.currentTask);

        const badge = document.getElementById('drawer-step-badge');
        const title = document.getElementById('drawer-title');
        const conf = document.getElementById('drawer-confidence');
        const url = document.getElementById('drawer-provenance-url');
        const gaz = document.getElementById('drawer-gazette-ref');
        const dept = document.getElementById('drawer-dept-name');
        const addr = document.getElementById('drawer-office-addr');
        const hours = document.getElementById('drawer-office-hours');
        const sla = document.getElementById('drawer-sla-days');
        const desc = document.getElementById('drawer-step-desc');
        const docs = document.getElementById('drawer-docs-list');
        const forms = document.getElementById('drawer-forms-list');
        const fees = document.getElementById('drawer-fee-breakdown');
        const btnComplete = document.getElementById('btn-toggle-complete');

        if (badge) badge.innerText = isMr ? `टप्पा ${step.step_number}` : `Step ${step.step_number}`;
        if (title) title.innerText = stepTitle;
        if (conf && step.verification_source) conf.innerText = `${(step.verification_source.confidence_score * 100).toFixed(0)}% Match`;
        if (url && step.verification_source) {
            url.href = step.verification_source.url || '#';
            url.innerText = step.verification_source.url || 'portal.gov.in';
        }
        if (gaz) gaz.innerText = isMr ? `वैधानिक प्राधिकरण: ${step.last_gazette_notification || 'महाराष्ट्र लोकसेवा हक्क अधिनियम'}` : `Statutory Authority: ${step.last_gazette_notification || (step.verification_source && step.verification_source.gazette_ref) || 'State Public Service Code'}`;
        if (dept) dept.innerText = deptName;
        if (addr) addr.innerText = step.department.office_address || `${deptName}, ${muniName}`;
        if (hours) hours.innerText = isMr ? 'सोम-शुक्र सकाळी १०:०० ते दुपारी ४:००' : (step.department.working_hours || 'Mon-Fri 10:00 AM - 4:00 PM IST');
        if (sla) sla.innerText = isMr ? `${step.estimated_days} दिवस` : `${step.estimated_days} Days`;
        if (desc) desc.innerText = stepDesc;

        if (docs) {
            docs.innerHTML = step.documents.map(d => `<div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>${this.getDocName(d.name)}</strong></div>`).join('') || (isMr ? 'काहीही नाही' : 'None');
        }
        if (forms) {
            forms.innerHTML = step.forms.map(f => `<div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>${f.form_code}</strong>: ${f.title}</div>`).join('') || (isMr ? 'काहीही नाही' : 'None');
        }
        if (fees) {
            fees.innerHTML = Object.entries(step.fee_breakdown).map(([k, v]) => `<div>${k}: <strong>${this.formatINR(v)}</strong></div>`).join('') || `${isMr ? 'एकूण' : 'Total'}: ${this.formatINR(step.fee_amount)}`;
        }

        if (btnComplete) {
            const isCompleted = this.completedStepIds.has(step.id);
            const compLabel = isMr ? 'पूर्ण झाले ✓' : 'Completed ✓';
            const markLabel = isMr ? 'टप्पा पूर्ण झाला म्हणून नोंदवा' : 'Mark Step Completed';
            btnComplete.innerHTML = isCompleted ? `<span class="material-symbols-outlined text-[16px]">done_all</span><span>${compLabel}</span>` : `<span class="material-symbols-outlined text-[16px]">check_circle</span><span>${markLabel}</span>`;
            btnComplete.className = isCompleted ? 'flex-1 bg-emerald-800 text-on-primary font-headline text-xs font-semibold py-2.5 px-3 flex items-center justify-center gap-1.5' : 'flex-1 bg-primary hover:bg-primary-container text-on-primary font-headline text-xs font-semibold py-2.5 px-3 flex items-center justify-center gap-1.5 transition-colors';
        }
    }

    openDrawer(stepId) {
        this.selectStation(stepId);
        const drawer = document.getElementById('step-drawer');
        const backdrop = document.getElementById('drawer-backdrop');
        if (drawer) drawer.classList.add('open');
        if (backdrop) backdrop.classList.add('open');
    }

    closeDrawer() {
        const drawer = document.getElementById('step-drawer');
        const backdrop = document.getElementById('drawer-backdrop');
        if (drawer) drawer.classList.remove('open');
        if (backdrop) backdrop.classList.remove('open');
    }

    inspectFullDossier() {
        this.switchNavTab('step-dossier');
    }

    inspectFullDossierFromDrawer() {
        this.closeDrawer();
        this.switchNavTab('step-dossier');
    }

    // -------------------------------------------------------------------------
    // Universal Procedural Milestone Advancement & Application Validator
    // -------------------------------------------------------------------------
    async advanceStepAction() {
        const inputRef = document.getElementById('statutory-app-num') || document.getElementById('mcgm-app-num');
        const isSelfDeclared = document.getElementById('chk-self-declaration')?.checked;
        const val = inputRef ? inputRef.value.trim() : '';

        // Validation: Alphanumeric min 4 chars OR self-declaration checkbox
        const isValidInput = val.length >= 4 && /^[a-zA-Z0-9\-\/_]+$/.test(val);

        if (!isValidInput && !isSelfDeclared) {
            alert('Procedural Notice: Please enter a valid Application Reference / Challan Number (at least 4 alphanumeric characters) or check the self-declaration box before completing this milestone.');
            if (inputRef) inputRef.focus();
            return;
        }

        const stepId = this.selectedStationId;
        const refNumber = val || `SELF-DECL-${Date.now().toString().slice(-6)}`;
        
        // Save application reference
        this.stepApplicationNumbers[stepId] = refNumber;
        this.saveTaskAppNums();

        // Advance milestone
        this.completedStepIds.add(stepId);
        this.inProgressStepIds.delete(stepId);
        this.saveTaskCompleted();
        this.saveTaskInProgress();

        alert(`Application / Reference #${refNumber} recorded. Milestone "${stepId}" marked as Cleared & Verified.`);

        // Find next incomplete step to select
        const steps = this.currentTask.steps;
        const currIdx = steps.findIndex(s => s.id === stepId);
        if (currIdx >= 0 && currIdx < steps.length - 1) {
            this.selectedStationId = steps[currIdx + 1].id;
        }

        await this.loadRoadmap(this.currentTaskId);
    }

    async toggleStepComplete(stepId) {
        return this.toggleStepCompletion(stepId);
    }

    async toggleStepCompletion(stepId) {
        if (this.completedStepIds.has(stepId)) {
            this.completedStepIds.delete(stepId);
            delete this.stepApplicationNumbers[stepId];
        } else {
            this.completedStepIds.add(stepId);
            this.inProgressStepIds.delete(stepId);
            if (!this.stepApplicationNumbers[stepId]) {
                this.stepApplicationNumbers[stepId] = `CIVIC-ACK-${Date.now().toString().slice(-6)}`;
            }
        }
        this.saveTaskCompleted();
        this.saveTaskInProgress();
        this.saveTaskAppNums();

        await this.loadRoadmap(this.currentTaskId);
        this.updateStationUI();
    }

    toggleWayfindingView(mode) {
        const subwayWrapper = document.getElementById('subway-diagram-wrapper');
        const dagWrapper = document.getElementById('dag-canvas-wrapper');
        const btnSubway = document.getElementById('btn-mode-subway');
        const btnDag = document.getElementById('btn-mode-dag');

        if (mode === 'cards') {
            if (subwayWrapper) subwayWrapper.style.display = 'none';
            if (dagWrapper) dagWrapper.style.display = 'none';
            return;
        }

        if (mode === 'subway') {
            const isCurrentlyShown = subwayWrapper && subwayWrapper.style.display === 'block';
            if (isCurrentlyShown && this.wayfindingMode === 'subway') {
                if (subwayWrapper) subwayWrapper.style.display = 'none';
                return;
            }
            this.wayfindingMode = 'subway';
            if (subwayWrapper) subwayWrapper.style.display = 'block';
            if (dagWrapper) dagWrapper.style.display = 'none';
            if (btnSubway) {
                btnSubway.className = 'px-3 py-1.5 rounded font-semibold bg-primary text-white';
            }
            if (btnDag) {
                btnDag.className = 'px-3 py-1.5 rounded font-semibold text-gray-700 hover:text-primary';
            }
            if (this.subwayRenderer && this.currentTask && this.currentRoadmap) {
                this.subwayRenderer.render(
                    this.currentTask,
                    this.currentRoadmap,
                    this.completedStepIds,
                    this.selectedStationId
                );
            }
        } else if (mode === 'dag') {
            this.wayfindingMode = 'dag';
            if (subwayWrapper) subwayWrapper.style.display = 'none';
            if (dagWrapper) dagWrapper.style.display = 'block';
            if (btnSubway) {
                btnSubway.className = 'px-3 py-1.5 rounded font-semibold text-gray-700 hover:text-primary';
            }
            if (btnDag) {
                btnDag.className = 'px-3 py-1.5 rounded font-semibold bg-primary text-white';
            }
            setTimeout(() => this.visualizer.fitToScreen(), 50);
        }
    }

    toggleCriticalPathHighlight() {
        this.criticalPathActive = !this.criticalPathActive;
        const btn = document.getElementById('btn-toggle-critical');
        const txt = document.getElementById('txt-critical');

        if (btn) btn.classList.toggle('bg-primary', this.criticalPathActive);
        if (btn) btn.classList.toggle('text-on-primary', this.criticalPathActive);
        if (txt) txt.innerText = this.criticalPathActive ? 'Highlighting Critical Path' : 'Show Critical Path Only';

        this.visualizer.toggleCriticalPath(this.criticalPathActive);

        // Re-render Subway Map with Critical Path highlight
        if (this.subwayRenderer && this.currentTask && this.currentRoadmap) {
            this.subwayRenderer.render(
                this.currentTask,
                this.currentRoadmap,
                this.completedStepIds,
                this.selectedStationId
            );
        }
    }

    // -------------------------------------------------------------------------
    // Dynamic Citizen Compliance Ledger
    // -------------------------------------------------------------------------
    renderCitizenLedger() {
        if (!this.currentTask) return;

        const isMr = (this.currentLang === 'mr');
        const task = this.currentTask;
        const steps = task.steps || [];
        const clearedSteps = steps.filter(s => this.completedStepIds.has(s.id));
        const cleared = clearedSteps.length;
        const totalFees = steps.reduce((sum, s) => sum + (s.fee_amount || 0), 0);
        const paidFees = clearedSteps.reduce((sum, s) => sum + (s.fee_amount || 0), 0);
        const pendingFees = Math.max(0, totalFees - paidFees);
        const pendingSteps = steps.filter(s => !this.completedStepIds.has(s.id));
        const remainingDays = pendingSteps.reduce((sum, s) => sum + (s.estimated_days || 0), 0);

        // Header metrics
        const elTaskTitle = document.getElementById('ledger-task-title');
        const elCleared = document.getElementById('ledger-steps-cleared');
        const elTotal = document.getElementById('ledger-steps-total');
        const elTotalFees = document.getElementById('ledger-total-fees');
        const elPaidFees = document.getElementById('ledger-fees-paid');
        const elPendingFees = document.getElementById('ledger-fees-pending');
        const elDaysRemaining = document.getElementById('ledger-days-remaining');

        if (elTaskTitle) elTaskTitle.innerText = this.getTaskTitle(task);
        if (elCleared) elCleared.innerText = `${cleared}`;
        if (elTotal) elTotal.innerText = `${steps.length}`;
        if (elTotalFees) elTotalFees.innerText = this.formatINR(totalFees);
        if (elPaidFees) elPaidFees.innerText = this.formatINR(paidFees);
        if (elPendingFees) elPendingFees.innerText = this.formatINR(pendingFees);
        if (elDaysRemaining) elDaysRemaining.innerText = `${remainingDays} ${isMr ? 'दिवस' : 'Days'}`;

        // 1. Render Left Steps Checklist
        const stepsContainer = document.getElementById('ledger-steps-list');
        if (stepsContainer) {
            stepsContainer.innerHTML = steps.map((s, idx) => {
                const isDone = this.completedStepIds.has(s.id);
                const stepTitle = this.getStepTitle(s, task.id);
                const deptName = this.getStepDept(s, task.id);
                const feeText = s.fee_amount > 0 ? this.formatINR(s.fee_amount) : (isMr ? 'विनामूल्य' : 'Free');
                const slaText = isMr ? `${s.estimated_days} दिवस` : `${s.estimated_days} Days`;
                const statusBadge = isDone
                    ? `<span class="bg-emerald-100 text-emerald-800 text-[11px] px-2 py-0.5 rounded font-semibold font-headline">${isMr ? '✓ पूर्ण' : '✓ Completed'}</span>`
                    : `<span class="bg-amber-100 text-amber-900 text-[11px] px-2 py-0.5 rounded font-semibold font-headline">${isMr ? 'प्रलंबित' : 'Pending'}</span>`;
                const btnDetails = isMr ? 'तपशील' : 'Details';

                return `
                    <div class="p-3.5 border border-outline-variant rounded-md flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${isDone ? 'bg-emerald-50/30' : 'bg-surface-container-lowest'}">
                        <div class="flex items-start gap-3">
                            <input type="checkbox" ${isDone ? 'checked' : ''} onchange="window.app.toggleStepComplete('${s.id}')" class="mt-1 w-4 h-4 text-emerald-700 rounded border-outline focus:ring-emerald-600 cursor-pointer">
                            <div>
                                <div class="font-headline text-xs font-semibold text-primary flex items-center gap-2">
                                    <span class="${isDone ? 'line-through text-gray-500' : ''}">${idx + 1}. ${stepTitle}</span>
                                </div>
                                <div class="font-body text-[11px] text-secondary mt-0.5">${deptName} • ⏱️ ${slaText} • 💰 ${feeText}</div>
                            </div>
                        </div>
                        <div class="flex items-center gap-2 self-end sm:self-center shrink-0">
                            ${statusBadge}
                            <button onclick="window.app.selectStation('${s.id}'); window.app.switchNavTab('step-dossier');" class="bg-surface-container hover:bg-surface-container-high text-primary px-2.5 py-1 rounded text-[11px] font-semibold font-headline border border-outline-variant">
                                ${btnDetails} ↗
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // 2. Render Right Document Locker List
        const docsContainer = document.getElementById('ledger-docs-list');
        if (docsContainer) {
            const allDocs = (this.currentRoadmap && this.currentRoadmap.consolidated_documents) || [];
            if (allDocs.length === 0) {
                docsContainer.innerHTML = `<div class="p-4 text-xs text-secondary font-headline">${isMr ? 'या प्रक्रियेसाठी अतिरिक्त कागदपत्रे आवश्यक नाहीत.' : 'No statutory documents required for this procedure.'}</div>`;
            } else {
                docsContainer.innerHTML = allDocs.map(d => {
                    const isReady = this.checkedDocIds.has(d.name);
                    const docName = this.getDocName(d.name);
                    const safeName = d.name.replace(/'/g, "\\'");
                    const badge = isReady
                        ? `<span class="bg-emerald-100 text-emerald-800 text-[10px] px-2 py-0.5 rounded font-semibold font-headline">${isMr ? '✓ तयार' : '✓ In File'}</span>`
                        : `<span class="bg-amber-100 text-amber-900 text-[10px] px-2 py-0.5 rounded font-semibold font-headline">${isMr ? 'गहाळ' : 'Missing'}</span>`;
                    const mandatoryLabel = d.is_mandatory ? (isMr ? 'अनिवार्य' : 'Mandatory') : (isMr ? 'ऐच्छिक' : 'Optional');

                    return `
                        <div class="p-3 border border-outline-variant rounded-md flex items-center justify-between gap-3 ${isReady ? 'bg-emerald-50/20' : 'bg-surface-container-lowest'}">
                            <label class="flex items-start gap-2.5 cursor-pointer flex-1">
                                <input type="checkbox" ${isReady ? 'checked' : ''} onchange="window.app.toggleDocumentReady('${safeName}')" class="mt-1 w-4 h-4 text-emerald-700 rounded border-outline focus:ring-emerald-600">
                                <div>
                                    <div class="font-headline text-xs font-semibold text-primary ${isReady ? 'line-through text-gray-500' : ''}">${docName}</div>
                                    <div class="font-code text-[10px] text-secondary mt-0.5">${mandatoryLabel} • ${d.category || 'General'}</div>
                                </div>
                            </label>
                            <div class="shrink-0">${badge}</div>
                        </div>
                    `;
                }).join('');
            }
        }
    }

    // -------------------------------------------------------------------------
    // Dual-Track NLP Intent Resolution & Procedure Search
    // -------------------------------------------------------------------------
    async performSearch() {
        const queryInput = document.getElementById('taskQuery');
        const jurSelect = document.getElementById('jurisdictionSelect');
        const btnSubmit = document.getElementById('btn-generate-roadmap');
        const q = queryInput ? queryInput.value.trim() : '';
        const jur = jurSelect ? jurSelect.value : '';

        if (!q) {
            this.switchNavTab('roadmap-and-route');
            return;
        }

        // Show loading spinner on button
        const originalBtnHtml = btnSubmit ? btnSubmit.innerHTML : '';
        const isMr = (this.currentLang === 'mr');
        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = `
                <span class="material-symbols-outlined text-[18px] animate-spin">sync</span>
                <span>${isMr ? 'वैधानिक प्रक्रिया शोधत आहे...' : 'Resolving Statutory Intent...'}</span>
            `;
        }

        try {
            const resp = await fetch('/api/tasks/resolve-intent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: q, municipality: jur })
            });

            if (!resp.ok) {
                throw new Error(`HTTP error ${resp.status}`);
            }

            const data = await resp.json();
            console.log('NLP Intent Resolution Result:', data);

            // Render interactive search feedback cards on Intake Screen
            this.renderNlpResolutionFeedback(data);

            if (data.needs_disambiguation && data.matches && data.matches.length >= 2) {
                // Multi-candidate disambiguation required: do NOT auto-redirect!
                // Stay on Intake Screen and smoothly focus the disambiguation options
                const feedbackEl = document.getElementById('nlp-search-feedback');
                if (feedbackEl) {
                    feedbackEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
                return;
            }

            if (data.top_task_id) {
                // Set provenance notice for the roadmap header banner
                if (data.hinglish_detected) {
                    this.lastSearchNotice = {
                        type: 'hinglish',
                        message: isMr 
                            ? `स्थानिक भाषा शब्द शोधले: अधिकृत वैधानिक संज्ञेशी जोडले ("${data.normalized_query}").`
                            : `Hinglish query detected: Interpreted and mapped to statutory terms ("${data.normalized_query}").`
                    };
                } else if (data.synthesis) {
                    this.lastSearchNotice = {
                        type: 'synthesized',
                        message: isMr
                            ? `"${data.original_query}" साठी वैधानिक नियमांनुसार प्रक्रिया मार्ग तयार केला.`
                            : `Zero-shot statutory route dynamically synthesized for "${data.original_query}". Formulated pursuant to statutory rules.`
                    };
                } else {
                    this.lastSearchNotice = null;
                }

                await this.loadTaskAndRoute(data.top_task_id);
            } else {
                await this.loadTaskAndRoute('task-mum-bakery');
            }
        } catch (err) {
            console.error('NLP Intent Resolution failed, falling back to Maharashtra heuristic:', err);
            const qLower = q.toLowerCase();
            if (qLower.includes('pune') || qLower.includes('pmc')) {
                await this.loadTaskAndRoute('task-pune-restaurant');
            } else if (qLower.includes('7/12') || qLower.includes('satbara') || qLower.includes('mutation') || qLower.includes('ferfar')) {
                await this.loadTaskAndRoute('task-mah-712-mutation');
            } else if (qLower.includes('water') || qLower.includes('pani') || qLower.includes('nal')) {
                await this.loadTaskAndRoute('task-mum-water-connection');
            } else if (qLower.includes('certificate') || qLower.includes('dakhla') || qLower.includes('aaple sarkar') || qLower.includes('income')) {
                await this.loadTaskAndRoute('task-mah-rts-certificates');
            } else if (qLower.includes('construction') || qLower.includes('autodcr') || qLower.includes('building')) {
                await this.loadTaskAndRoute('task-mum-construction');
            } else if (qLower.includes('bakery') || qLower.includes('bandra')) {
                await this.loadTaskAndRoute('task-mum-bakery');
            } else {
                await this.loadTaskAndRoute('task-mah-small-biz');
            }
        } finally {
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = originalBtnHtml;
            }
        }
    }

    fillQuery(text) {
        const inp = document.getElementById('taskQuery');
        if (inp) {
            inp.value = text;
        }
        this.performSearch();
    }

    renderNlpResolutionFeedback(data) {
        const container = document.getElementById('nlp-search-feedback');
        if (!container) return;

        if (!data || !data.matches || data.matches.length === 0) {
            container.classList.add('hidden');
            return;
        }

        container.classList.remove('hidden');
        const isMr = (this.currentLang === 'mr');

        let disambiguationBannerHtml = '';
        if (data.needs_disambiguation && data.matches.length >= 2) {
            const optA = data.matches[0];
            const optB = data.matches[1];
            const optATitle = (isMr && window.TASK_TRANSLATIONS?.[optA.task_id]?.title) || optA.title;
            const optBTitle = (isMr && window.TASK_TRANSLATIONS?.[optB.task_id]?.title) || optB.title;
            disambiguationBannerHtml = `
                <div class="p-4 bg-amber-50 border-2 border-amber-500 rounded shadow-xs mb-3 space-y-3">
                    <div class="flex items-center gap-2 text-amber-900 font-bold text-sm">
                        <span class="material-symbols-outlined text-amber-600">help_outline</span>
                        <span>${isMr ? 'कृपया वैधानिक हेतू स्पष्ट करा (अस्पष्ट शोध पर्याय):' : 'Ambiguous Statutory Intent — Please Clarify Your Request:'}</span>
                    </div>
                    <p class="text-xs text-amber-800">
                        ${isMr 
                            ? `आपला शोध एकापेक्षा जास्त अधिकृत प्रक्रियेशी जवळपास समान पातळीवर जुळत आहे. कृपया आपला अचूक पर्याय निवडा:` 
                            : `Your query closely matches multiple distinct civic workflows. Please select your intended procedure:`}
                    </p>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                        <button onclick="window.app.loadTaskAndRoute('${optA.task_id}')" 
                                class="flex items-center justify-between p-3 bg-white border border-amber-300 hover:border-primary hover:bg-amber-100/40 text-left transition-all rounded shadow-2xs group">
                            <div>
                                <span class="font-bold text-xs text-primary block group-hover:underline">Option A: ${optATitle}</span>
                                <span class="text-[11px] text-gray-500">${optA.municipality} • ${optA.category}</span>
                            </div>
                            <span class="material-symbols-outlined text-[18px] text-primary shrink-0 ml-2 group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
                        </button>
                        <button onclick="window.app.loadTaskAndRoute('${optB.task_id}')" 
                                class="flex items-center justify-between p-3 bg-white border border-amber-300 hover:border-primary hover:bg-amber-100/40 text-left transition-all rounded shadow-2xs group">
                            <div>
                                <span class="font-bold text-xs text-primary block group-hover:underline">Option B: ${optBTitle}</span>
                                <span class="text-[11px] text-gray-500">${optB.municipality} • ${optB.category}</span>
                            </div>
                            <span class="material-symbols-outlined text-[18px] text-primary shrink-0 ml-2 group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
                        </button>
                    </div>
                </div>
            `;
        }

        let hinglishBadgeHtml = '';
        if (data.hinglish_detected) {
            hinglishBadgeHtml = `
                <div class="flex items-center gap-2 p-2 bg-amber-50 border border-amber-300 text-amber-900 rounded-none text-xs">
                    <span class="material-symbols-outlined text-[16px] text-amber-700">translate</span>
                    <span><strong>${isMr ? 'स्थानिक व बोलीभाषा शब्द शोधले:' : 'Hinglish / Regional Terms Detected:'}</strong> ${isMr ? 'या संदर्भात अर्थ लावला:' : 'Interpreted as:'} <em class="font-code text-[11px] font-semibold">${data.normalized_query}</em></span>
                </div>
            `;
        }

        const matchCardsHtml = data.matches.slice(0, 3).map((m) => {
            const isSynth = m.match_type === 'synthesized';
            const pct = Math.round(m.confidence * 100);
            const badgeClass = isSynth
                ? 'bg-purple-100 text-purple-900 border border-purple-300'
                : (pct >= 70 ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-blue-100 text-blue-900 border border-blue-300');
            const typeLabel = isSynth 
                ? (isMr ? 'एआय थेट संश्लेषण' : 'AI Zero-Shot Synthesis') 
                : `${pct}% ${isMr ? 'जुळणारे परिणाम' : 'Semantic Match'}`;

            const taskTrans = (window.TASK_TRANSLATIONS && window.TASK_TRANSLATIONS[m.task_id]) || {};
            const title = (isMr && taskTrans.title) ? taskTrans.title : m.title;
            const muni = (isMr && (taskTrans.municipality || window.MUNI_TRANSLATIONS?.[m.municipality])) ? (taskTrans.municipality || window.MUNI_TRANSLATIONS?.[m.municipality]) : m.municipality;
            const cat = (isMr && taskTrans.category) ? taskTrans.category : m.category;
            const btnText = isMr ? 'मार्ग पहा' : 'Load Route';

            return `
                <div class="p-2.5 bg-surface-container-lowest border border-outline-variant hover:border-primary transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div class="space-y-0.5">
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="font-code text-[10px] px-1.5 py-0.5 font-bold ${badgeClass}">${typeLabel}</span>
                            <span class="text-xs font-semibold text-primary">${title}</span>
                        </div>
                        <p class="text-[11px] text-on-surface-variant line-clamp-1">${muni} • ${cat}</p>
                    </div>
                    <button class="bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold px-3 py-1.5 transition-colors shrink-0 flex items-center gap-1"
                            onclick="window.app.loadTaskAndRoute('${m.task_id}')">
                        <span>${btnText}</span>
                        <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </button>
                </div>
            `;
        }).join('');

        const headerLabel = isMr ? `वैधानिक प्रक्रिया शोधली (${data.matches.length} परिणाम):` : `Statutory Intent Resolved (${data.matches.length} matches):`;
        container.innerHTML = `
            ${disambiguationBannerHtml}
            ${hinglishBadgeHtml}
            <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-wider">
                ${headerLabel}
            </div>
            <div class="space-y-1.5">
                ${matchCardsHtml}
            </div>
        `;
    }

    // -------------------------------------------------------------------------
    // Indian Currency & Date Formatting Helpers
    // -------------------------------------------------------------------------
    formatINR(amount) {
        const num = parseFloat(amount) || 0;
        return '₹' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    formatDateIN(isoStr) {
        if (!isoStr) return '24-09-2026';
        try {
            const d = new Date(isoStr);
            if (isNaN(d.getTime())) return isoStr.split('T')[0];
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const year = d.getFullYear();
            return `${day}-${month}-${year}`;
        } catch (e) {
            return isoStr;
        }
    }

    // -------------------------------------------------------------------------
    // Dynamic Document Readiness Locker & Expiry Guard
    // -------------------------------------------------------------------------
    renderDocumentLocker() {
        const listContainer = document.getElementById('document-locker-list');
        const labelScore = document.getElementById('locker-readiness-label');
        const pctScore = document.getElementById('locker-readiness-pct');
        const progressBar = document.getElementById('locker-progress-bar');
        const deficitAlert = document.getElementById('locker-deficit-alert');
        const headingDesc = document.getElementById('locker-heading-desc');
        const filterContainer = document.getElementById('locker-category-filters');
        
        if (!this.currentRoadmap || !this.currentTask) return;
        const isMr = (this.currentLang === 'mr');
        const allDocs = this.currentRoadmap.consolidated_documents || [];
        const totalCount = allDocs.length;
        const readyCount = allDocs.filter(d => this.checkedDocIds.has(d.name)).length;
        const pct = totalCount > 0 ? Math.round((readyCount / totalCount) * 100) : 0;
        const muniName = this.getTaskMunicipality(this.currentTask);

        // Dynamic Header Description
        if (headingDesc) {
            headingDesc.innerText = isMr
                ? `सर्व ${this.currentTask.steps.length} टप्प्यांसाठी आवश्यक सर्व शासकीय कागदपत्रांची एकत्रित सूची. अर्ज फेटाळला जाऊ नये म्हणून ${muniName} कार्यालयात जाण्यापूर्वी डिजिटल किंवा मूळ कागदपत्रे तयार ठेवा.`
                : `Consolidated multi-agency document inventory required across all ${this.currentTask.steps.length} procedural milestones. Audit your physical file or DigiLocker records before visiting ${this.currentTask.municipality} counters to eliminate rejection delays.`;
        }

        // Update counts & progress
        if (labelScore) labelScore.innerText = isMr ? `${readyCount} / ${totalCount} कागदपत्रे तयार (${pct}%)` : `${readyCount} / ${totalCount} Documents Ready (${pct}%)`;
        if (pctScore) pctScore.innerText = `${pct}%`;
        if (progressBar) progressBar.style.width = `${pct}%`;
        
        // Summary stat badge on roadmap
        const elDocs = document.getElementById('summary-stat-docs');
        if (elDocs) elDocs.innerText = `${readyCount} / ${totalCount}`;

        // Deficit alert banner
        if (deficitAlert) {
            if (readyCount === totalCount && totalCount > 0) {
                deficitAlert.className = 'text-emerald-900 font-semibold bg-emerald-50 border border-emerald-300 px-2 py-0.5';
                deficitAlert.innerHTML = isMr ? '✓ पूर्ण दस्तऐवज संच: सर्व आवश्यक कागदपत्रे तयार आहेत.' : '✓ Complete Physical File: All statutory documents prepared for official submission.';
            } else {
                deficitAlert.className = 'text-amber-900 font-semibold bg-amber-50 border border-amber-300 px-2 py-0.5';
                deficitAlert.innerHTML = isMr ? `⚠ कागदपत्रे अपुरी: ${totalCount - readyCount} अनिवार्य कागदपत्रे अद्याप बाकी आहेत.` : `⚠ File Deficit: ${totalCount - readyCount} mandatory documents still missing from physical file.`;
            }
        }

        // Dynamic Category Filter Tabs from actual consolidated_documents
        if (filterContainer) {
            const categories = Array.from(new Set(allDocs.map(d => d.category || 'General'))).filter(Boolean);
            const allLabel = isMr ? `सर्व कागदपत्रे (${totalCount})` : `All Documents (${totalCount})`;
            
            // Build buttons: 'All' + each non-empty category
            let buttonsHtml = `
                <button onclick="window.app.filterDocumentLocker('all')" class="locker-filter-btn px-3 py-1.5 ${this.activeDocCategory === 'all' ? 'bg-primary text-on-primary' : 'bg-surface-container text-primary'} font-semibold shrink-0" data-category="all">
                    ${allLabel}
                </button>
            `;

            categories.forEach(cat => {
                const count = allDocs.filter(d => d.category === cat).length;
                if (count > 0) {
                    const isActive = this.activeDocCategory === cat;
                    buttonsHtml += `
                        <button onclick="window.app.filterDocumentLocker('${cat.replace(/'/g, "\'")}')" class="locker-filter-btn px-3 py-1.5 ${isActive ? 'bg-primary text-on-primary font-semibold' : 'bg-surface-container hover:bg-surface-container-high text-primary border border-outline-variant'} shrink-0" data-category="${cat}">
                            ${cat} (${count})
                        </button>
                    `;
                }
            });

            filterContainer.innerHTML = buttonsHtml;
        }

        if (!listContainer) return;

        // Filter list
        const filteredDocs = this.activeDocCategory === 'all' 
            ? allDocs 
            : allDocs.filter(d => d.category === this.activeDocCategory);

        if (filteredDocs.length === 0) {
            listContainer.innerHTML = `<div class="col-span-2 p-6 bg-surface-container-lowest border border-outline-variant text-secondary text-sm">${isMr ? 'या श्रेणीत कागदपत्रे नाहीत.' : 'No documents found in this category.'}</div>`;
            return;
        }

        listContainer.innerHTML = filteredDocs.map(d => {
            const isReady = this.checkedDocIds.has(d.name);
            const stepNums = d.required_in_step_numbers || d.required_in_steps || [];
            const stepsLabel = stepNums.length > 0
                ? stepNums.map(sNum => (isMr ? `टप्पा 0${sNum}` : `Stop 0${sNum}`)).join(', ')
                : (isMr ? 'सामान्य टप्पा' : 'General Milestone');

            const safeDocName = d.name.replace(/'/g, "\'");
            const docName = this.getDocName(d.name);
            const mandatoryLabel = d.is_mandatory ? (isMr ? 'अनिवार्य' : 'Mandatory') : (isMr ? 'ऐच्छिक' : 'Optional');
            const inBagBadge = isReady ? (isMr ? '✓ तयार' : '✓ In File') : (isMr ? 'गहाळ' : 'Missing');
            const toggleActionText = isReady ? (isMr ? 'गहाळ म्हणून नोंदवा' : 'Mark as Missing') : (isMr ? 'तयार म्हणून खूण करा' : 'Mark as Ready in Bag');

            return `
                <div class="doc-card ${isReady ? 'ready' : 'missing'} p-4 border border-outline-variant flex flex-col justify-between gap-3 shadow-sm">
                    <div class="space-y-2">
                        <div class="flex items-start justify-between gap-3">
                            <label class="flex items-start gap-2.5 cursor-pointer flex-1">
                                <input type="checkbox" ${isReady ? 'checked' : ''} onchange="window.app.toggleDocumentReady('${safeDocName}')" class="mt-1 w-4 h-4 text-emerald-700 rounded border-outline focus:ring-emerald-600">
                                <div>
                                    <div class="font-headline text-sm font-semibold text-primary ${isReady ? 'line-through opacity-75' : ''}">${docName}</div>
                                    <div class="flex items-center gap-1.5 flex-wrap mt-1">
                                        <span class="font-code text-[10px] px-1.5 py-0.2 bg-surface-container text-secondary font-semibold border border-outline-variant">${d.category || 'General'}</span>
                                        ${d.is_mandatory ? `<span class="font-headline text-[10px] px-1.5 py-0.2 bg-red-100 text-red-900 border border-red-300 font-bold">${mandatoryLabel}</span>` : `<span class="font-headline text-[10px] px-1.5 py-0.2 bg-surface-container text-secondary">${mandatoryLabel}</span>`}
                                        <span class="font-code text-[10px] text-secondary">${isMr ? 'आवश्यक:' : 'Required at:'} <strong>${stepsLabel}</strong></span>
                                    </div>
                                </div>
                            </label>
                            <span class="font-headline text-[11px] px-2 py-0.5 font-bold ${isReady ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-amber-100 text-amber-900 border border-amber-300'} shrink-0">
                                ${inBagBadge}
                            </span>
                        </div>

                        <p class="font-body text-xs text-on-surface-variant leading-relaxed pl-6">
                            ${d.description}
                        </p>

                        ${d.validity_rule ? `
                            <div class="ml-6 p-2 bg-surface-container-low border border-outline-variant text-[11px] font-body text-primary flex items-center gap-1.5">
                                <span class="material-symbols-outlined text-amber-700 text-[14px]">warning</span>
                                <span><strong>${isMr ? 'वैधता / स्वरूप नियम:' : 'Validity / Format Rule:'}</strong> ${d.validity_rule}</span>
                            </div>
                        ` : ''}
                    </div>

                    <div class="ml-6 pt-2 border-t border-outline-variant flex items-center justify-between text-[11px] font-headline">
                        <span class="text-secondary font-code">${isMr ? 'डिजीलॉकर / स्व-साक्षांकित प्रत' : 'DigiLocker / Self-Attested Copy'}</span>
                        <button class="text-primary hover:text-secondary font-semibold underline" onclick="window.app.toggleDocumentReady('${safeDocName}')">
                            ${toggleActionText}
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    toggleDocumentReady(docName) {
        if (this.checkedDocIds.has(docName)) {
            this.checkedDocIds.delete(docName);
        } else {
            this.checkedDocIds.add(docName);
        }
        this.saveTaskDocs();
        this.renderDocumentLocker();
        this.updateHeaderAndStats();
    }

    filterDocumentLocker(category) {
        this.activeDocCategory = category;
        this.renderDocumentLocker();
    }

    resetDocumentChecklist() {
        const isMr = (this.currentLang === 'mr');
        if (confirm(isMr ? 'कागदपत्र यादी रीसेट करायची का? सर्व कागदपत्रे पडताळणीसाठी पुन्हा गहाळ म्हणून नोंदवली जातील.' : 'Reset citizen document bag? All documents will be marked as missing for pre-visit audit.')) {
            this.checkedDocIds.clear();
            this.saveTaskDocs();
            this.renderDocumentLocker();
            this.updateHeaderAndStats();
        }
    }

    // -------------------------------------------------------------------------
    // Verification Staleness Sentinel & Direct Counter Discrepancy Reporting
    // -------------------------------------------------------------------------
    openDiscrepancyModal(stepId) {
        const sId = stepId || this.selectedStationId;
        const step = (this.currentTask && this.currentTask.steps.find(s => s.id === sId)) || (this.currentTask && this.currentTask.steps[0]);
        if (!step) return;

        this.selectedStationId = step.id;
        const isMr = (this.currentLang === 'mr');
        const stepTitle = this.getStepTitle(step, this.currentTask.id);
        const deptName = this.getStepDept(step, this.currentTask.id);
        const muniName = this.getTaskMunicipality(this.currentTask);

        const elTargetStep = document.getElementById('discrepancy-target-step');
        const elTargetAgency = document.getElementById('discrepancy-target-agency');
        const elRecordedVal = document.getElementById('discrepancy-recorded-val');
        const elDemandedVal = document.getElementById('discrepancy-demanded-val');
        const elNotes = document.getElementById('discrepancy-notes');
        const elContact = document.getElementById('discrepancy-contact');

        if (elTargetStep) elTargetStep.innerText = isMr ? `टप्पा ०${step.step_number}: ${stepTitle}` : `Stop 0${step.step_number}: ${step.title}`;
        if (elTargetAgency) elTargetAgency.innerText = `${deptName} — ${step.department.office_address || step.department.jurisdiction || muniName}`;
        if (elRecordedVal) elRecordedVal.value = isMr 
            ? `अधिकृत शासकीय शुल्क: ${this.formatINR(step.fee_amount)} | हमी कालावधी: ${step.estimated_days} दिवस` 
            : `Official Fee: ${this.formatINR(step.fee_amount)} | SLA: ${step.estimated_days} Days`;
        if (elDemandedVal) elDemandedVal.value = '';
        if (elNotes) elNotes.value = '';
        if (elContact) elContact.value = '';

        const modal = document.getElementById('modal-discrepancy');
        if (modal) {
            modal.classList.add('open');
            if (elDemandedVal) elDemandedVal.focus();
        }
    }

    closeDiscrepancyModal() {
        const modal = document.getElementById('modal-discrepancy');
        if (modal) {
            modal.classList.remove('open');
        }
    }

    async submitDiscrepancyReport() {
        const isMr = (this.currentLang === 'mr');
        const cat = document.getElementById('discrepancy-category')?.value || 'Fee Discrepancy';
        const demanded = document.getElementById('discrepancy-demanded-val')?.value.trim() || '';
        const notes = document.getElementById('discrepancy-notes')?.value.trim() || '';
        const contact = document.getElementById('discrepancy-contact')?.value.trim() || '';

        if (!demanded || !notes) {
            alert(isMr ? 'कृपया प्रत्यक्ष मागणी केलेले शुल्क आणि तुमचे निरीक्षण नमूद करा.' : 'Please specify the demanded value and factual observations.');
            return;
        }

        const payload = {
            step_id: this.selectedStationId,
            issue_type: cat,
            notes: `[Demanded: ${demanded}] ${notes}${contact ? ' (Citizen Contact: ' + contact + ')' : ''}`
        };

        try {
            const resp = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                const auditRef = Math.floor(100000 + Math.random() * 900000);
                const targetMuni = (this.currentTask && this.getTaskMunicipality(this.currentTask)) || 'Municipal';
                alert(isMr 
                    ? `नागरिक तक्रार अहवाल यशस्वीरित्या नोंदवला गेला.\n\nऑडिट संदर्भ: #DISC-${auditRef}\nप्रशासकीय पडताळणीसाठी ${targetMuni} दक्षता कक्षाकडे पाठवला गेला.`
                    : `Citizen Discrepancy Report submitted successfully.\n\nAudit Ref: #DISC-${auditRef}\nTransmitted to ${targetMuni} Grievance & Vigilance Cell for administrative verification.`);
                this.closeDiscrepancyModal();
                if (this.admin && typeof this.admin.loadFeedback === 'function') {
                    this.admin.loadFeedback();
                }
            } else {
                alert(isMr ? 'अहवाल सादर करण्यात त्रुटी आली. कृपया पुन्हा प्रयत्न करा.' : 'Failed to submit report. Please try again.');
            }
        } catch (e) {
            console.error('Feedback submit error', e);
            alert(isMr ? 'कनेक्शन त्रुटी. अहवाल सादर होऊ शकला नाही.' : 'Connection error submitting report.');
        }
    }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CivicApp();
});
