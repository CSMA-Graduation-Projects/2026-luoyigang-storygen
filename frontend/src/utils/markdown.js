import { marked } from "marked"
import hljs from "highlight.js"
import "highlight.js/styles/github.css"

marked.setOptions({
    breaks: true,
    highlight: (code) => hljs.highlightAuto(code).value
})

export const renderMarkdown = (text) => {
    return marked.parse(text || "")
}