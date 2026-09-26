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

window.CivicGraphVisualizer = CivicGraphVisualizer;
