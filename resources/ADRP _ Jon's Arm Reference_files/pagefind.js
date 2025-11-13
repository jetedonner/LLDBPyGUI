const pagefindRoot = document.getElementById("search");
let pagefindInput = undefined;

window.addEventListener("DOMContentLoaded", (_) => {
    new PagefindUI({
        element: "#" + pagefindRoot.id,
        showSubResults: false,
        resetStyles: false,
        translations: {
            placeholder: "Search... (CTRL/CMD+K)",
            load_more: "Load more results...",
            zero_results: 'No results for "[SEARCH_TERM]".',
            many_results: '[COUNT] results for "[SEARCH_TERM]".',
            one_result: '[COUNT] result for "[SEARCH_TERM]".',
            searching: 'Searching for "[SEARCH_TERM]"...',
        },
    });

    pagefindInput = pagefindRoot.getElementsByTagName("input")[0];
    pagefindInput.setAttribute("spellcheck", "false");
});

window.addEventListener("keydown", (event) => {
    event.stopImmediatePropagation();
    if (event.key == "k" && (event.ctrlKey || event.metaKey)) {
        pagefindInput.focus();
    }
});
