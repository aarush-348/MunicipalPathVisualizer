/**
 * Interactive SVG DAG Graph Visualizer Engine
 * Grounded in Civic Functionalism & Municipal Ledger discipline.
 */
class CivicGraphVisualizer {
    constructor(svgElementId, onNodeSelectCallback) {
        this.svg = document.getElementById(svgElementId);
        this.onNodeSelect = onNodeSelectCallback;
        
        this.nodes = [];
        this.edges = [];
        this.phases = [];
        this.selectedNodeId = null;
        this.criticalPathOnly = false;
        
        // Pan & Zoom Transform state
        this.scale = 0.82;
        this.translateX = 40;
        this.translateY = 80;
        this.isPanning = false;
        this.startX = 0;
        this.startY = 0;

        this.nodeWidth = 320;
        this.nodeHeight = 140;

        this._initSvgDefs();
        this._bindEvents();
    }

    _initSvgDefs() {
        if (!this.svg) return;
        this.svg.innerHTML = `
            <defs>
                <filter id="civic-card-shadow" x="-5%" y="-5%" width="115%" height="120%">
                    <feDropShadow dx="3" dy="3" stdDeviation="0" flood-color="#152238" flood-opacity="0.15"/>
                </filter>

                <!-- Arrowhead Markers -->
                <marker id="arrow-default" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 9 5 L 0 9 z" fill="#51606f" />
                </marker>
                <marker id="arrow-critical" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                    <path d="M 0 1 L 9 5 L 0 9 z" fill="#d9a441" />
                </marker>
                <marker id="arrow-active" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                    <path d="M 0 1 L 9 5 L 0 9 z" fill="#2f6848" />
                </marker>
            </defs>
            <g id="viewport">
                <g id="phases-layer"></g>
                <g id="edges-layer"></g>
                <g id="nodes-layer"></g>
            </g>
        `;
        this.viewport = this.svg.querySelector('#viewport');
        this.phasesLayer = this.svg.querySelector('#phases-layer');
        this.edgesLayer = this.svg.querySelector('#edges-layer');
        this.nodesLayer = this.svg.querySelector('#nodes-layer');
    }

    _bindEvents() {
        if (!this.svg) return;
        this.svg.addEventListener('mousedown', (e) => {
            if (e.target.closest('.node-card')) return;
            this.isPanning = true;
            this.startX = e.clientX - this.translateX;
            this.startY = e.clientY - this.translateY;
        });

        window.addEventListener('mousemove', (e) => {
            if (!this.isPanning) return;
            this.translateX = e.clientX - this.startX;
            this.translateY = e.clientY - this.startY;
            this._updateTransform();
        });

        window.addEventListener('mouseup', () => {
            this.isPanning = false;
        });

        this.svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = 1.1;
            const mouseX = e.offsetX;
            const mouseY = e.offsetY;

            let newScale = e.deltaY < 0 ? this.scale * zoomFactor : this.scale / zoomFactor;
            newScale = Math.max(0.35, Math.min(2.0, newScale));

            this.translateX = mouseX - (mouseX - this.translateX) * (newScale / this.scale);
            this.translateY = mouseY - (mouseY - this.translateY) * (newScale / this.scale);
            this.scale = newScale;

            this._updateTransform();
        });
    }

    _updateTransform() {
        if (this.viewport) {
            this.viewport.setAttribute('transform', `translate(${this.translateX}, ${this.translateY}) scale(${this.scale})`);
        }
    }

    setRoadmapData(roadmap) {
        this.nodes = roadmap.nodes;
        this.edges = roadmap.edges;
        this.phases = roadmap.phases;
        this.render();
        this.fitToScreen();
    }

    toggleCriticalPath(active) {
        this.criticalPathOnly = active;
        this.render();
    }

    fitToScreen() {
        if (!this.nodes.length || !this.svg) return;
        const xs = this.nodes.map(n => n.x);
        const ys = this.nodes.map(n => n.y);
        const minX = Math.min(...xs);
        const maxX = Math.max(...xs) + this.nodeWidth;
        const minY = Math.min(...ys);
        const maxY = Math.max(...ys) + this.nodeHeight;

        const svgRect = this.svg.getBoundingClientRect();
        if (svgRect.width === 0 || svgRect.height === 0) return;

        const graphWidth = maxX - minX + 160;
        const graphHeight = maxY - minY + 160;

        const scaleX = svgRect.width / graphWidth;
        const scaleY = svgRect.height / graphHeight;
        this.scale = Math.max(0.4, Math.min(1.0, Math.min(scaleX, scaleY)));

        this.translateX = (svgRect.width - (maxX - minX) * this.scale) / 2 - minX * this.scale;
        this.translateY = (svgRect.height - (maxY - minY) * this.scale) / 2 - minY * this.scale;
        this._updateTransform();
    }

    resetView() {
        this.scale = 0.82;
        this.translateX = 40;
        this.translateY = 80;
        this._updateTransform();
    }

    zoomIn() {
        this.scale = Math.min(2.0, this.scale * 1.2);
        this._updateTransform();
    }

    zoomOut() {
        this.scale = Math.max(0.35, this.scale / 1.2);
        this._updateTransform();
    }

    render() {
        if (!this.nodesLayer) return;
        this.nodesLayer.innerHTML = '';
        this.edgesLayer.innerHTML = '';
        this.phasesLayer.innerHTML = '';

        this._renderPhaseHeaders();
        this._renderEdges();
        this._renderNodes();
    }

    _renderPhaseHeaders() {
        if (!this.phases) return;
        const xSpacing = 390;
        this.phases.forEach((phase) => {
            const px = phase.phase_index * xSpacing + 60;
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.innerHTML = `
                <rect x="${px}" y="10" width="${this.nodeWidth + 20}" height="40" rx="3" fill="#edf2f6" stroke="#cbd5e1" stroke-width="1"/>
                <text x="${px + 12}" y="28" fill="#152238" font-family="'IBM Plex Sans'" font-size="11" font-weight="700" letter-spacing="0.5">${phase.title.toUpperCase()}</text>
                <text x="${px + 12}" y="42" fill="#51606f" font-family="'Source Serif 4'" font-size="10">${phase.description.substring(0, 52)}...</text>
            `;
            this.phasesLayer.appendChild(g);
        });
    }

    _renderEdges() {
        const nodeMap = new Map(this.nodes.map(n => [n.id, n]));

        this.edges.forEach(edge => {
            const sourceNode = nodeMap.get(edge.source);
            const targetNode = nodeMap.get(edge.target);
            if (!sourceNode || !targetNode) return;

            const x1 = sourceNode.x + this.nodeWidth;
            const y1 = sourceNode.y + (this.nodeHeight / 2);
            const x2 = targetNode.x;
            const y2 = targetNode.y + (this.nodeHeight / 2);

            const dx = Math.max(70, (x2 - x1) * 0.5);
            const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', d);
            path.setAttribute('id', edge.id);
            path.setAttribute('fill', 'none');

            let strokeColor = '#cbd5e1';
            let strokeWidth = '2';
            let strokeDash = 'none';
            let marker = 'url(#arrow-default)';

            if (edge.is_critical) {
                strokeColor = '#d9a441';
                strokeWidth = '3';
                marker = 'url(#arrow-critical)';
            }
            if (sourceNode.status === 'completed') {
                strokeColor = '#2f6848';
                strokeWidth = '2.5';
                marker = 'url(#arrow-active)';
            }

            if (this.criticalPathOnly && !edge.is_critical) {
                path.setAttribute('opacity', '0.12');
            }

            path.setAttribute('stroke', strokeColor);
            path.setAttribute('stroke-width', strokeWidth);
            path.setAttribute('stroke-dasharray', strokeDash);
            path.setAttribute('marker-end', marker);
            this.edgesLayer.appendChild(path);
        });
    }

    _renderNodes() {
        this.nodes.forEach(node => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', `node-card ${node.status} cursor-pointer`);
            g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
            g.setAttribute('data-id', node.id);

            // Styling tokens per Stitch design
            let borderColor = '#cbd5e1';
            let leftBarColor = '#152238';
            let statusPillBg = '#f3f4f2';
            let statusPillText = '#51606f';
            let statusLabel = 'LOCKED';
            let statusIcon = '🔒';

            if (node.status === 'completed') {
                borderColor = '#2f6848';
                leftBarColor = '#2f6848';
                statusPillBg = '#edf6f0';
                statusPillText = '#1d4a32';
                statusLabel = 'CLEARED';
                statusIcon = '✓';
            } else if (node.status === 'ready') {
                borderColor = '#d9a441';
                leftBarColor = '#d9a441';
                statusPillBg = '#fdf3e7';
                statusPillText = '#8a5800';
                statusLabel = 'READY TO START';
                statusIcon = '⚡';
            } else if (node.status === 'in_progress') {
                borderColor = '#152238';
                leftBarColor = '#d9a441';
                statusPillBg = '#fdf3e7';
                statusPillText = '#8a5800';
                statusLabel = 'IN PROGRESS';
                statusIcon = '⏳';
            }

            if (node.is_critical_path && node.status !== 'completed') {
                borderColor = '#d9a441';
            }

            const truncatedTitle = node.title.length > 36 ? node.title.substring(0, 34) + '...' : node.title;
            const truncatedDept = node.department_name.length > 38 ? node.department_name.substring(0, 36) + '...' : node.department_name;
            const feeStr = node.fee_amount > 0 ? `₹${node.fee_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : 'Fee Exempt';

            g.innerHTML = `
                <!-- Background Paper Container -->
                <rect class="node-bg" width="${this.nodeWidth}" height="${this.nodeHeight}" rx="4" 
                      fill="#ffffff" stroke="${borderColor}" stroke-width="1" filter="url(#civic-card-shadow)"/>
                
                <!-- Left Structural Color Spine -->
                <rect x="0" y="0" width="4" height="${this.nodeHeight}" rx="2" fill="${leftBarColor}"/>

                <!-- Header: Step # & Status Badge -->
                <circle cx="26" cy="24" r="11" fill="#152238"/>
                <text x="26" y="28" fill="#ffffff" font-family="'IBM Plex Sans'" font-size="11" font-weight="700" text-anchor="middle">${node.step_number}</text>

                <!-- Status Pill -->
                <rect x="46" y="15" width="105" height="18" rx="2" fill="${statusPillBg}" stroke="${borderColor}" stroke-width="0.5"/>
                <text x="52" y="27" fill="${statusPillText}" font-family="'IBM Plex Sans'" font-size="9.5" font-weight="700">${statusIcon} ${statusLabel}</text>

                <!-- Official Verification Stamp -->
                <rect x="${this.nodeWidth - 110}" y="15" width="98" height="18" rx="2" fill="#edf6f0" stroke="#2f6848" stroke-width="0.5"/>
                <text x="${this.nodeWidth - 61}" y="27" fill="#1d4a32" font-family="'IBM Plex Sans'" font-size="9" font-weight="700" text-anchor="middle">✓ STATUTORY SEAL</text>

                <!-- Step Title -->
                <text x="16" y="60" fill="#152238" font-family="'IBM Plex Sans'" font-size="13" font-weight="700">${truncatedTitle}</text>

                <!-- Department Name -->
                <text x="16" y="78" fill="#51606f" font-family="'Source Serif 4'" font-size="11.5">${truncatedDept}</text>

                <!-- Horizontal Divider Line -->
                <line x1="12" y1="94" x2="${this.nodeWidth - 12}" y2="94" stroke="#d8dfe6" stroke-width="1"/>

                <!-- Bottom Metadata: SLA & Fee & Mode -->
                <text x="16" y="117" fill="#152238" font-family="'JetBrains Mono'" font-size="10.5" font-weight="600">⏱ ${node.estimated_days} Days</text>
                <text x="110" y="117" fill="#8a5800" font-family="'JetBrains Mono'" font-size="10.5" font-weight="700">💳 ${feeStr}</text>
                <rect x="${this.nodeWidth - 84}" y="104" width="72" height="18" rx="2" fill="#f3f4f2" stroke="#cbd5e1" stroke-width="0.5"/>
                <text x="${this.nodeWidth - 48}" y="116" fill="#152238" font-family="'IBM Plex Sans'" font-size="9.5" font-weight="600" text-anchor="middle">${node.submission_mode}</text>
            `;

            g.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectNode(node.id);
            });

            this.nodesLayer.appendChild(g);
        });
    }

    selectNode(nodeId) {
        this.selectedNodeId = nodeId;
        if (this.onNodeSelect) {
            this.onNodeSelect(nodeId);
        }
    }
}

/**
 * Dynamic Subway Transit Map Renderer
 * Programmatically builds interactive subway transit route maps with casing trunk lines,
 * dynamic branch forks, interchange stations, and status indicators for ANY civic task.
 */
class CivicSubwayRenderer {
    constructor(svgId, onSelectCallback) {
        this.svg = document.getElementById(svgId);
        this.onSelect = onSelectCallback;
    }

    render(task, roadmap, completedStepIds, selectedStationId) {
        if (!this.svg || !task || !task.steps || task.steps.length === 0) return;

        const steps = task.steps;
        const totalSteps = steps.length;
        
        // Dynamic SVG dimensions based on step count
        const colWidth = totalSteps <= 4 ? 220 : (totalSteps <= 6 ? 160 : 135);
        const svgHeight = 360;
        const centerY = 180;

        // Compute topological depth for each step based on prerequisites
        const stepDepths = {};
        steps.forEach((s) => {
            if (!s.prerequisites || s.prerequisites.length === 0) {
                stepDepths[s.id] = 0;
            } else {
                const maxParent = Math.max(...s.prerequisites.map(p => stepDepths[p] !== undefined ? stepDepths[p] : 0));
                stepDepths[s.id] = maxParent + 1;
            }
        });

        // Group steps by depth
        const depthGroups = {};
        steps.forEach(s => {
            const d = stepDepths[s.id] || 0;
            if (!depthGroups[d]) depthGroups[d] = [];
            depthGroups[d].push(s);
        });

        const depthsList = Object.keys(depthGroups).map(Number).sort((a, b) => a - b);
        const totalDepths = Math.max(depthsList.length, 1);
        const svgWidth = Math.max(940, 160 + totalDepths * colWidth);

        this.svg.setAttribute('viewBox', `0 0 ${svgWidth} ${svgHeight}`);

        const colSpacing = (svgWidth - 180) / Math.max(totalDepths - 1, 1);
        const stepPositions = {};

        // Assign X and Y for each step
        depthsList.forEach((depth, colIdx) => {
            const groupSteps = depthGroups[depth];
            const x = 90 + colIdx * colSpacing;
            
            if (groupSteps.length === 1) {
                stepPositions[groupSteps[0].id] = { x, y: centerY, step: groupSteps[0] };
            } else {
                const spread = Math.min(110, 240 / (groupSteps.length - 1 || 1));
                const startY = centerY - ((groupSteps.length - 1) * spread) / 2;
                groupSteps.forEach((s, idx) => {
                    stepPositions[s.id] = { x, y: startY + idx * spread, step: s };
                });
            }
        });

        // Structural grid marks
        let gridLinesHtml = '';
        for (let gx = 90; gx <= svgWidth - 70; gx += 140) {
            gridLinesHtml += `<line x1="${gx}" x2="${gx}" y1="20" y2="${svgHeight - 20}"></line>`;
        }

        // Draw connecting track segments
        let tracksCasingHtml = '';
        let tracksCoreHtml = '';
        const drawnEdges = new Set();

        steps.forEach((s, idx) => {
            const targetPos = stepPositions[s.id];
            const isTargetDone = completedStepIds.has(s.id);
            const isTargetActive = selectedStationId === s.id;

            const sources = (s.prerequisites && s.prerequisites.length > 0)
                ? s.prerequisites
                : (idx > 0 ? [steps[idx - 1].id] : []);

            sources.forEach(srcId => {
                const srcPos = stepPositions[srcId];
                if (!srcPos) return;

                const edgeKey = `${srcId}->${s.id}`;
                if (drawnEdges.has(edgeKey)) return;
                drawnEdges.add(edgeKey);

                const x1 = srcPos.x;
                const y1 = srcPos.y;
                const x2 = targetPos.x;
                const y2 = targetPos.y;

                let pathD = '';
                if (Math.abs(y1 - y2) < 5) {
                    pathD = `M ${x1} ${y1} L ${x2} ${y2}`;
                } else {
                    const cx1 = x1 + (x2 - x1) * 0.45;
                    const cx2 = x1 + (x2 - x1) * 0.55;
                    pathD = `M ${x1} ${y1} C ${cx1} ${y1}, ${cx2} ${y2}, ${x2} ${y2}`;
                }

                // Casing
                tracksCasingHtml += `<path d="${pathD}" fill="none" stroke="#152238" stroke-width="12" stroke-linecap="round"/>`;

                // Core stroke color
                let coreColor = '#CBD5E1';
                let strokeDash = '';
                let coreWidth = '6';

                if (isTargetDone) {
                    coreColor = '#2F6848'; // green cleared
                } else if (isTargetActive || completedStepIds.has(srcId)) {
                    coreColor = '#D9A441'; // gold active
                    strokeDash = 'stroke-dasharray="6,4"';
                    coreWidth = '5';
                }

                tracksCoreHtml += `<path d="${pathD}" fill="none" stroke="${coreColor}" stroke-width="${coreWidth}" ${strokeDash} stroke-linecap="round"/>`;
            });
        });

        // Station nodes
        let stationsHtml = '';
        steps.forEach((s, idx) => {
            const pos = stepPositions[s.id];
            const x = pos.x;
            const y = pos.y;
            const isDone = completedStepIds.has(s.id);
            const isSelected = selectedStationId === s.id;
            const stepNum = s.step_number < 10 ? `0${s.step_number}` : `${s.step_number}`;
            const cleanTitle = s.title.length > 25 ? s.title.substring(0, 23) + '...' : s.title;

            let nodeGraphics = '';
            let statusLabel = '';
            let statusColor = '#75777E';

            if (isDone) {
                statusLabel = 'CLEARED';
                statusColor = '#2F6848';
                nodeGraphics = `
                    <circle cx="${x}" cy="${y}" r="16" fill="#152238"/>
                    <circle cx="${x}" cy="${y}" r="12" fill="#2F6848"/>
                    <path d="M ${x - 5} ${y} L ${x - 1} ${y + 4} L ${x + 6} ${y - 4}" fill="none" stroke="#FFFFFF" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/>
                `;
            } else if (isSelected) {
                statusLabel = 'ACTIVE STATION';
                statusColor = '#8A5800';
                nodeGraphics = `
                    <circle class="animate-pulse" cx="${x}" cy="${y}" r="24" fill="#D9A441" fill-opacity="0.3"/>
                    <circle cx="${x}" cy="${y}" r="18" fill="#152238"/>
                    <circle cx="${x}" cy="${y}" r="13" fill="#FFFFFF"/>
                    <circle cx="${x}" cy="${y}" r="8" fill="#D9A441"/>
                `;
            } else {
                statusLabel = `${s.estimated_days}D • PENDING`;
                statusColor = '#5C6B7A';
                nodeGraphics = `
                    <circle cx="${x}" cy="${y}" r="16" fill="#152238"/>
                    <circle cx="${x}" cy="${y}" r="12" fill="#FFFFFF"/>
                    <circle cx="${x}" cy="${y}" r="6" fill="#5C6B7A"/>
                `;
            }

            const labelAbove = (y < centerY) || (y === centerY && idx % 2 === 1);
            const titleY = labelAbove ? y - 34 : y + 36;
            const subY = labelAbove ? y - 20 : y + 50;

            stationsHtml += `
                <g class="cursor-pointer group" onclick="window.app.selectStation('${s.id}')">
                    ${nodeGraphics}
                    <text x="${x}" y="${titleY}" font-family="'IBM Plex Sans'" font-size="11.5" font-weight="${isSelected ? '700' : '600'}" text-anchor="middle" fill="#152238">${stepNum}. ${cleanTitle}</text>
                    <text x="${x}" y="${subY}" font-family="'JetBrains Mono'" font-size="9.5" font-weight="600" text-anchor="middle" fill="${statusColor}">${statusLabel}</text>
                </g>
            `;
        });

        this.svg.innerHTML = `
            <g stroke="#e2e3e1" stroke-dasharray="2,6" stroke-width="1">
                ${gridLinesHtml}
            </g>
            ${tracksCasingHtml}
            ${tracksCoreHtml}
            ${stationsHtml}
        `;
    }
}

window.CivicGraphVisualizer = CivicGraphVisualizer;
window.CivicSubwayRenderer = CivicSubwayRenderer;

