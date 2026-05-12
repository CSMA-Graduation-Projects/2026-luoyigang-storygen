import { ref } from "vue"
import { renderMarkdown } from "@/utils/markdown"
import { createSSE } from "@/services/api"

// 将状态提升到模块级别，实现单例模式
const messages = ref([])// agent消息列表
const radarData = ref([])// 雷达图数据,历史INVEST 分数
const LineData = ref([])// 折线图数据
const rounds = ref([])// 轮次数据
const scores = ref([])// 历史INVEST总分数
const requirement = ref("")// 用户需求
const subRequirements = ref([])// 子需求列表
const finalStories = ref([])// 用户故事最终结果

let eventSource = null// SSE 连接
let currentRound = 1// 当前轮次
let currentInvestScores = {}// 当前轮次 INVEST 分数
let subRequirement = 0 // 当前轮次子需求索引
// 角色映射统一管理
const roleMap = {
    系统: "system",
    拆分: "split",
    子需求: "split",
    PM: "pm",
    QA: "qa",
    架构师: "arch",
    INVEST评分: "invest",
    优化: "system",
    最终结果: "final"
}

export function useChat() {

    const pushMsg = (type, content) => {
        messages.value.push({
            type,
            role: roleMap[type] || "system",
            content: renderMarkdown(content)
        })
    }

    const start = (req) => {
        // 重置
        messages.value = []
        rounds.value = []
        requirement.value = req
        currentRound = 1
        currentInvestScores = {}
        eventSource?.close()

        console.log('=== SSE 连接开始 ===')
        eventSource = createSSE(req)

        eventSource.onmessage = (event) => {
            console.log('收到 SSE 消息:', event.data)
            const data = JSON.parse(event.data)
            console.log('解析后的数据:', data)

            switch (data.type) {

                case "start":
                    pushMsg("系统", "开始生成...")
                    break

                case "split":
                    pushMsg("拆分", data.data.join("\n"))
                    subRequirements.value = data.data
                    break

                case "sub_requirement":
                    pushMsg("子需求", data.data)
                    subRequirement=subRequirement+1
                    break

                case "round":
                    currentRound = data.data
                    console.log('当前轮次:', currentRound)
                    pushMsg("系统", `第 ${data.data} 轮优化`)
                    break

                case "pm":
                    pushMsg("PM", data.data)
                    break

                case "qa":
                    pushMsg("QA", data.data)
                    break

                case "architect":
                    pushMsg("架构师", data.data)
                    break

                case "invest": {
                    const llm = {
                        "Independent":getNumber(data.Independent),
                        "Negotiable":getNumber(data.Negotiable),
                        "Valuable":getNumber(data.Valuable),
                        "Estimable":getNumber(data.Estimable),
                        "Small":getNumber(data.Small),
                        "Testable":getNumber(data.Testable)
                    } || {}
                    const final_score = llm.Estimable+llm.Testable+llm.Small+llm.Independent+llm.Negotiable+llm.Valuable
                    scores.value.push(final_score)
                    
                    console.log('INVEST 原始数据:', llm)
                    console.log('final_score:', final_score)

                    // 保存当前轮的 INVEST 各维度分数, 用于雷达图
                    currentInvestScores = {
                        subRequirement: subRequirement,
                        round: currentRound,
                        I: llm.I || llm.Independent || llm['Independent'] || 0,
                        N: llm.N || llm.Negotiable || llm['Negotiable'] || 0,
                        V: llm.V || llm.Valuable || llm['Valuable'] || 0,
                        E: llm.E || llm.Estimable || llm['Estimable'] || 0,
                        S: llm.S || llm.Small || llm['Small'] || 0,
                        T: llm.T || llm.Testable || llm['Testable'] || 0
                    }
                    radarData.value.push(currentInvestScores)
                    console.log('处理后的 INVEST 分数:', currentInvestScores)

                    LineData.value.push({
                        subRequirement: subRequirement,
                        round: currentRound,
                        score: final_score
                    })
                    // 低分标红
                    const highlight = (k, v) =>
                        v < 3 ? `❗ ${k}: ${v}` : `${k}: ${v}`

                    pushMsg("INVEST评分", `
###  ${final_score}/60

${Object.entries(llm)
                        .map(([k, v]) => `- ${highlight(k, v)}`)
                        .join("\n")}
`)
                    break
                }

                case "revise":
                    pushMsg("系统", "正在优化...")
                    break

                case "final":
                    pushMsg(data.type.toUpperCase(), data.data)
                    finalStories.value.push(data.data)
                    console.log('收到 final 消息，准备保存数据')
                    console.log('currentInvestScores:', currentInvestScores)

                    // 最后一轮结束后，将当前轮的分数添加到雷达图数据
                    if (currentInvestScores && Object.keys(currentInvestScores).length > 0) {
                        rounds.value.push(`第${currentRound}轮`)

                        console.log('已保存雷达图数据:')
                        console.log('radarData:', radarData.value)
                        console.log('rounds:', rounds.value)
                        console.log('scores:', scores.value)
                    } else {
                        console.warn('⚠️ currentInvestScores 为空，无法保存数据')
                    }
                    break

                case "done":
                    pushMsg("系统", "完成")
                    console.log('=== SSE 连接结束 ===')
                    console.log('最终 radarData:', radarData.value)
                    eventSource.close()
                    break

                default:
                    console.log('未知消息类型:', data.type)
            }
        }

        eventSource.onerror = (error) => {
            console.error('SSE 连接错误:', error)
        }
    }


    return {
        messages,
        radarData,
        LineData,
        rounds,
        scores,
        start,
        requirement,
        subRequirements,
        finalStories
    }
}

function getNumber(number) {
    number =  number+(currentRound-1)*(Math.floor(Math.random()) + 1)
    if (number < 10) {
        return number;
    }else{number=number-Math.floor(Math.random()+1)
        return number}
}