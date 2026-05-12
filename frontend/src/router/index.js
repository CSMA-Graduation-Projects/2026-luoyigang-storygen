import { createRouter, createWebHistory } from "vue-router"

import ChatView from "../views/ChatView.vue"
import RadarView from "../views/RadarView.vue"
import LineView from "../views/LineView.vue"
import AgentView from "@/views/AgentView.vue"
import CodeStoryView from "@/views/CodeStoryView.vue"
import DocumentStoryView from "@/views/DocumentStoryView.vue"
import ProjectStoryView from "@/views/ProjectStoryView.vue"
import UserStoryOptimizationView from "@/views/UserStoryOptimizationView.vue"
import HistoryStoryView from "@/views/HistoryStoryView.vue"

const routes = [
    { path: "/", component: ChatView },
    { path: "/code-story", component: CodeStoryView },
    { path: "/document-story", component: DocumentStoryView },
    { path: "/project-story", component: ProjectStoryView },
    { path: "/story-optimization", component: UserStoryOptimizationView },
    { path: "/analysis/radar", component: RadarView },
    { path: "/analysis/line", component: LineView },
    { path: "/history-stories", component: HistoryStoryView },
    { path: "/agent", component: AgentView },
]

export default createRouter({
    history: createWebHistory(),
    routes
})
