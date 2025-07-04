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
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importStar(require("react"));
const react_router_dom_1 = require("react-router-dom");
const MangaReaderModal_1 = __importDefault(require("./MangaReaderModal"));
const MangaDetails = () => {
    const { id, source } = (0, react_router_dom_1.useParams)();
    const [manga, setManga] = (0, react_1.useState)(null);
    const [loading, setLoading] = (0, react_1.useState)(true);
    const [error, setError] = (0, react_1.useState)('');
    const [readerOpen, setReaderOpen] = (0, react_1.useState)(false);
    const [readerImages, setReaderImages] = (0, react_1.useState)([]);
    const [readerTitle, setReaderTitle] = (0, react_1.useState)('');
    const [readerLoading, setReaderLoading] = (0, react_1.useState)(false);
    (0, react_1.useEffect)(() => {
        const fetchMangaDetails = () => __awaiter(void 0, void 0, void 0, function* () {
            try {
                setLoading(true);
                setError('');
                const response = yield fetch(`/api/manga/${source}/${id}`);
                if (!response.ok)
                    throw new Error('Failed to fetch manga details');
                const data = yield response.json();
                setManga(data);
            }
            catch (err) {
                setError(err.message || 'Failed to fetch manga details');
            }
            finally {
                setLoading(false);
            }
        });
        if (id && source)
            fetchMangaDetails();
    }, [id, source]);
    const handleChapterClick = (chapter) => __awaiter(void 0, void 0, void 0, function* () {
        setReaderLoading(true);
        setReaderOpen(true);
        setReaderTitle(chapter.title);
        try {
            const resp = yield fetch(`/api/chapter-images/${source}/${id}/${chapter.url}`);
            const data = yield resp.json();
            setReaderImages(data.images || []);
        }
        catch (_a) {
            setReaderImages([]);
        }
        finally {
            setReaderLoading(false);
        }
    });
    if (loading) {
        return (react_1.default.createElement("div", { className: "min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center" },
            react_1.default.createElement("div", { className: "text-lg text-gray-700 dark:text-gray-200" }, "Loading manga details...")));
    }
    if (error || !manga) {
        return (react_1.default.createElement("div", { className: "min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center" },
            react_1.default.createElement(react_router_dom_1.Link, { to: "/", className: "mb-4 text-purple-600 hover:underline" }, "\u2190 Back to Search"),
            react_1.default.createElement("div", { className: "text-lg text-red-500" }, error || 'Manga not found')));
    }
    return (react_1.default.createElement("div", { className: "min-h-screen bg-gray-50 dark:bg-gray-900" },
        react_1.default.createElement("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" },
            react_1.default.createElement("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-8" },
                react_1.default.createElement("div", { className: "lg:col-span-1" },
                    react_1.default.createElement("div", { className: "sticky top-24" },
                        react_1.default.createElement("div", { className: "bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden" },
                            react_1.default.createElement("div", { className: "aspect-[3/4] overflow-hidden bg-gray-100 dark:bg-gray-700" }, manga.image ? (react_1.default.createElement("img", { src: manga.image, alt: manga.title, className: "w-full h-full object-cover" })) : (react_1.default.createElement("div", { className: "w-full h-full flex items-center justify-center text-gray-400" },
                                react_1.default.createElement("div", { className: "text-center" },
                                    react_1.default.createElement("div", { className: "w-24 h-24 bg-gray-200 dark:bg-gray-600 rounded-lg mx-auto mb-4" }),
                                    react_1.default.createElement("span", null, "No Cover Available"))))),
                            react_1.default.createElement("div", { className: "p-6" },
                                react_1.default.createElement("div", { className: "mt-6 space-y-4" },
                                    react_1.default.createElement("div", null,
                                        react_1.default.createElement("span", { className: "text-sm font-medium text-gray-500 dark:text-gray-400" }, "Author"),
                                        react_1.default.createElement("div", { className: "mt-1 text-gray-900 dark:text-white" }, manga.author)),
                                    manga.status && (react_1.default.createElement("div", null,
                                        react_1.default.createElement("span", { className: "text-sm font-medium text-gray-500 dark:text-gray-400" }, "Status"),
                                        react_1.default.createElement("div", { className: "mt-1 text-gray-900 dark:text-white capitalize" }, manga.status))),
                                    manga.url && (react_1.default.createElement("div", null,
                                        react_1.default.createElement("span", { className: "text-sm font-medium text-gray-500 dark:text-gray-400" }, "Source"),
                                        react_1.default.createElement("div", { className: "mt-1" },
                                            react_1.default.createElement("a", { href: manga.url, target: "_blank", rel: "noopener noreferrer", className: "text-purple-600 hover:underline" },
                                                "View on ",
                                                manga.source ? manga.source.charAt(0).toUpperCase() + manga.source.slice(1) : 'Source'))))))))),
                react_1.default.createElement("div", { className: "lg:col-span-2 space-y-8" },
                    react_1.default.createElement("div", { className: "bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6" },
                        react_1.default.createElement("h1", { className: "text-3xl font-bold text-gray-900 dark:text-white mb-4" }, manga.title),
                        react_1.default.createElement("div", { className: "prose prose-gray dark:prose-invert max-w-none" },
                            react_1.default.createElement("p", { className: "text-gray-700 dark:text-gray-300 leading-relaxed" }, manga.description))),
                    react_1.default.createElement("div", { className: "bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700" },
                        react_1.default.createElement("div", { className: "p-6 border-b border-gray-200 dark:border-gray-700" },
                            react_1.default.createElement("div", { className: "flex items-center justify-between" },
                                react_1.default.createElement("h2", { className: "text-xl font-bold text-gray-900 dark:text-white" }, "Chapters"))),
                        react_1.default.createElement("div", { className: "p-6" }, manga.chapters && manga.chapters.length > 0 ? (react_1.default.createElement("div", { className: "space-y-2" }, manga.chapters.map((chapter, idx) => (react_1.default.createElement("button", { key: chapter.url + idx, onClick: () => handleChapterClick(chapter), className: "flex items-center justify-between w-full p-4 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors group text-left" },
                            react_1.default.createElement("div", { className: "flex items-center space-x-4" },
                                react_1.default.createElement("span", { className: "font-medium text-gray-900 dark:text-white" }, chapter.title),
                                chapter.date && (react_1.default.createElement("span", { className: "text-sm text-gray-500 dark:text-gray-400" }, chapter.date))),
                            react_1.default.createElement("span", { className: "text-purple-600 group-hover:text-purple-700" }, "Read \u2192")))))) : (react_1.default.createElement("div", { className: "text-gray-500 dark:text-gray-400" }, "No chapters found."))))))),
        react_1.default.createElement(MangaReaderModal_1.default, { open: readerOpen, images: readerImages, onClose: () => setReaderOpen(false), chapterTitle: readerTitle }),
        readerOpen && readerLoading && (react_1.default.createElement("div", { className: "manga-reader-loading" }, "Loading pages..."))));
};
exports.default = MangaDetails;
