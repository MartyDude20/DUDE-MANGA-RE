"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importStar(require("react"));
require("./MangaReaderModal.css");
const MODES = ['single', 'double', 'vertical'];
const MangaReaderModal = ({ open, images, onClose, chapterTitle }) => {
    const [showControls, setShowControls] = (0, react_1.useState)(true);
    const [viewMode, setViewMode] = (0, react_1.useState)('vertical');
    const [currentPage, setCurrentPage] = (0, react_1.useState)(0);
    (0, react_1.useEffect)(() => {
        if (!open)
            return;
        setCurrentPage(0);
        setViewMode('vertical');
    }, [open, images]);
    const totalPages = images ? images.length : 0;
    const progress = totalPages > 0 ? ((viewMode === 'double' ? currentPage + 2 : currentPage + 1) / totalPages) * 100 : 0;
    const nextPage = (0, react_1.useCallback)(() => {
        if (!images)
            return;
        const increment = viewMode === 'double' ? 2 : 1;
        setCurrentPage((prev) => Math.min(prev + increment, totalPages - 1));
    }, [images, viewMode, totalPages]);
    const prevPage = (0, react_1.useCallback)(() => {
        const decrement = viewMode === 'double' ? 2 : 1;
        setCurrentPage((prev) => Math.max(prev - decrement, 0));
    }, [viewMode]);
    const handleKeyPress = (0, react_1.useCallback)((e) => {
        if (!open)
            return;
        switch (e.key) {
            case 'Escape':
                onClose();
                break;
            case 'h':
            case 'H':
                setShowControls((prev) => !prev);
                break;
            case 'v':
            case 'V':
                setViewMode((prev) => {
                    const idx = MODES.indexOf(prev);
                    return MODES[(idx + 1) % MODES.length];
                });
                break;
            case 'ArrowRight':
            case ' ':
                if (viewMode === 'vertical') {
                    window.scrollBy(0, window.innerHeight * 0.8);
                }
                else {
                    nextPage();
                }
                break;
            case 'ArrowLeft':
                if (viewMode === 'vertical') {
                    window.scrollBy(0, -window.innerHeight * 0.8);
                }
                else {
                    prevPage();
                }
                break;
            default:
                break;
        }
    }, [open, onClose, viewMode, nextPage, prevPage]);
    (0, react_1.useEffect)(() => {
        if (!open)
            return;
        document.addEventListener('keydown', handleKeyPress);
        return () => document.removeEventListener('keydown', handleKeyPress);
    }, [open, handleKeyPress]);
    if (!open)
        return null;
    let content = null;
    if (viewMode === 'vertical') {
        content = (react_1.default.createElement("div", { className: "manga-reader-images manga-reader-vertical-images" }, images && images.length > 0 ? (images.map((src, idx) => (react_1.default.createElement("div", { key: src + idx, className: "manga-reader-image-wrapper" },
            react_1.default.createElement("img", { src: src, alt: `Page ${idx + 1}`, className: "manga-reader-image", loading: "lazy" }))))) : (react_1.default.createElement("div", { className: "manga-reader-no-pages" }, "No pages found."))));
    }
    else if (viewMode === 'single') {
        content = (react_1.default.createElement("div", { className: "manga-reader-images manga-reader-single-image" }, images && images.length > 0 ? (react_1.default.createElement("div", { className: "manga-reader-image-wrapper" },
            react_1.default.createElement("img", { src: images[currentPage], alt: `Page ${currentPage + 1}`, className: "manga-reader-image", loading: "lazy" }))) : (react_1.default.createElement("div", { className: "manga-reader-no-pages" }, "No pages found."))));
    }
    else if (viewMode === 'double') {
        content = (react_1.default.createElement("div", { className: "manga-reader-images manga-reader-double-images" }, images && images.length > 0 ? (react_1.default.createElement(react_1.default.Fragment, null,
            react_1.default.createElement("div", { className: "manga-reader-image-wrapper" },
                react_1.default.createElement("img", { src: images[currentPage], alt: `Page ${currentPage + 1}`, className: "manga-reader-image", loading: "lazy" }),
                currentPage + 1 < totalPages && (react_1.default.createElement("img", { src: images[currentPage + 1], alt: `Page ${currentPage + 2}`, className: "manga-reader-image", loading: "lazy" }))))) : (react_1.default.createElement("div", { className: "manga-reader-no-pages" }, "No pages found."))));
    }
    return (react_1.default.createElement("div", { className: "manga-reader-modal-overlay" },
        react_1.default.createElement("div", { className: `manga-reader-modal-content manga-reader-${viewMode}` },
            showControls && (react_1.default.createElement("div", { className: "manga-reader-header" },
                react_1.default.createElement("button", { className: "manga-reader-close", onClick: onClose }, "\u00D7"),
                react_1.default.createElement("h2", { className: "manga-reader-title" }, chapterTitle),
                react_1.default.createElement("div", { className: "manga-reader-progress-bar" },
                    react_1.default.createElement("div", { className: "manga-reader-progress", style: { width: `${progress}%` } })),
                react_1.default.createElement("div", { className: "manga-reader-controls" },
                    react_1.default.createElement("span", { className: "manga-reader-mode" },
                        viewMode.charAt(0).toUpperCase() + viewMode.slice(1),
                        " Mode"),
                    react_1.default.createElement("span", { className: "manga-reader-page-info" }, viewMode === 'double'
                        ? `${currentPage + 1}-${Math.min(currentPage + 2, totalPages)} / ${totalPages}`
                        : `${currentPage + 1} / ${totalPages}`),
                    react_1.default.createElement("button", { className: "manga-reader-toggle-controls", onClick: () => setShowControls((prev) => !prev), title: "Toggle Controls (H)" }, "Hide Controls"),
                    react_1.default.createElement("button", { className: "manga-reader-toggle-mode", onClick: () => setViewMode((prev) => {
                            const idx = MODES.indexOf(prev);
                            return MODES[(idx + 1) % MODES.length];
                        }), title: "Change View Mode (V)" }, "Change Mode")),
                react_1.default.createElement("div", { className: "manga-reader-nav-buttons" },
                    react_1.default.createElement("button", { className: "manga-reader-nav-btn", onClick: prevPage, disabled: currentPage === 0, title: "Previous Page (\u2190)" }, "\u2190"),
                    react_1.default.createElement("button", { className: "manga-reader-nav-btn", onClick: nextPage, disabled: currentPage >= totalPages - (viewMode === 'double' ? 2 : 1), title: "Next Page (\u2192 or Space)" }, "\u2192")))),
            content)));
};
exports.default = MangaReaderModal;
