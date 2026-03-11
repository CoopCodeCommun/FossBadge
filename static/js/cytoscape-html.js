/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["cytoscapeHtml"] = factory();
	else
		root["cytoscapeHtml"] = factory();
})(this, () => {
return /******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./src/collection/renderHTMLNodes.ts":
/*!*******************************************!*\
  !*** ./src/collection/renderHTMLNodes.ts ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ renderHTML)\n/* harmony export */ });\nfunction renderHTML(options) {\n    const cyto = this.cy();\n    const cytoContainer = cyto.container();\n    const nodeHtmlContainer = document.createElement(\"div\");\n    const internalId = \"__cytoscape-html__\";\n    const createNode = (node) => {\n        var _a;\n        const id = node.id();\n        const html = (_a = node.data()) === null || _a === void 0 ? void 0 : _a.html;\n        if (!html)\n            return;\n        const namespace = \"__cytoscape-html\";\n        const internalNodeId = `${namespace}_node-${id}`;\n        const position = node.renderedPosition();\n        const posX = position.x.toFixed(2);\n        const posY = position.y.toFixed(2);\n        const newNode = document.createElement(\"div\");\n        const existingNode = nodeHtmlContainer.querySelector(\"#\" + internalNodeId);\n        const nodeTranslation = `translate(${posX}px, ${posY}px)`;\n        const nodeScale = `scale(${cyto.zoom()})`;\n        const transform = `translate(-50%, -50%) ${nodeTranslation} ${nodeScale}`;\n        newNode.id = internalNodeId;\n        newNode.style.position = \"absolute\";\n        newNode.style.transform = transform;\n        newNode.style.zIndex = \"2\";\n        newNode.innerHTML = html;\n        if (existingNode)\n            nodeHtmlContainer.removeChild(existingNode);\n        nodeHtmlContainer.appendChild(newNode);\n        if (options.hideOriginal) {\n            // Hide the original node completely\n            node.style({\n                \"background-opacity\": 0,\n                \"border-opacity\": 0,\n                \"text-opacity\": 0,\n                \"overlay-opacity\": 0,\n            });\n        }\n    };\n    const removeNode = (node) => {\n        var _a;\n        const id = node.id();\n        const html = (_a = node.data()) === null || _a === void 0 ? void 0 : _a.html;\n        if (!html)\n            return;\n        const namespace = \"__cytoscape-html\";\n        const internalNodeId = `${namespace}_node-${id}`;\n        const existingNode = nodeHtmlContainer.querySelector(\"#\" + internalNodeId);\n        if (existingNode)\n            nodeHtmlContainer.removeChild(existingNode);\n    };\n    function handleMovement() {\n        cyto.nodes().forEach((node) => createNode(node));\n    }\n    if (!document.getElementById(internalId)) {\n        const canvas = cytoContainer.querySelector(\"canvas\");\n        nodeHtmlContainer.id = internalId;\n        canvas.parentNode.appendChild(nodeHtmlContainer);\n        nodeHtmlContainer.style.width = canvas.style.width;\n        nodeHtmlContainer.style.height = canvas.style.height;\n        nodeHtmlContainer.style.zIndex = \"1\";\n        cyto.on(\"add\", \"node\", (e) => createNode(e.target));\n        cyto.on(\"remove\", \"node\", (e) => removeNode(e.target));\n        cyto.on(\"drag\", \"node\", (e) => createNode(e.target));\n        cyto.on(\"pan resize\", handleMovement);\n    }\n    return cyto.nodes();\n}\n\n\n//# sourceURL=webpack://cytoscapeHtml/./src/collection/renderHTMLNodes.ts?\n}");

/***/ }),

/***/ "./src/cytoscape-html.ts":
/*!*******************************!*\
  !*** ./src/cytoscape-html.ts ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ register)\n/* harmony export */ });\n/* harmony import */ var _collection_renderHTMLNodes__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./collection/renderHTMLNodes */ \"./src/collection/renderHTMLNodes.ts\");\n\n// registers the extension on a cytoscape lib ref\nfunction register(cytoscape) {\n    // can't register if cytoscape unspecified\n    if (!cytoscape) {\n        return;\n    }\n    // register with cytoscape.js\n    cytoscape(\"collection\", \"renderHTMLNodes\", _collection_renderHTMLNodes__WEBPACK_IMPORTED_MODULE_0__[\"default\"]);\n}\nif (typeof window.cytoscape !== \"undefined\") {\n    register(window.cytoscape);\n}\n\n\n//# sourceURL=webpack://cytoscapeHtml/./src/cytoscape-html.ts?\n}");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./src/cytoscape-html.ts");
/******/ 	__webpack_exports__ = __webpack_exports__["default"];
/******/ 	
/******/ 	return __webpack_exports__;
/******/ })()
;
});