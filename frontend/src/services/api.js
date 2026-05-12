//const BASE_URL = 'http://localhost:8000'
const BASE_URL = '/api'

//原有 SSE 连接：文本需求到用户故事
export const createSSE = (requirement) => {
    const url = `${BASE_URL}/generate_story_stream?requirement=${encodeURIComponent(requirement)}`
    return new EventSource(url)
}

//代码片段到用户故事：独立代码解析，不复用文本需求生成流程
export const analyzeCodeStory = async (payload) => {
    const res = await fetch(`${BASE_URL}/code_story/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `代码用户故事生成失败：${res.status}`)
    }

    return await res.json()
}

//单个代码文件到用户故事：后端读取文件并分析
export const analyzeCodeStoryFile = async (file, language = '') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('language', language)

    const res = await fetch(`${BASE_URL}/code_story/analyze_file`, {
        method: 'POST',
        body: formData
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `代码文件用户故事生成失败：${res.status}`)
    }

    return await res.json()
}

//代码用户故事导出：Word / PDF / Markdown / JSON
export const exportCodeStory = async (codeStoryId, format = 'markdown') => {
    const res = await fetch(`${BASE_URL}/code_story/${codeStoryId}/export?format=${format}`)

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `代码用户故事导出失败：${res.status}`)
    }

    const filenameMap = {
        markdown: '代码逆向用户故事.md',
        md: '代码逆向用户故事.md',
        docx: '代码逆向用户故事.docx',
        pdf: '代码逆向用户故事.pdf',
        json: '代码逆向用户故事.json'
    }

    downloadBlob(await res.blob(), filenameMap[format] || filenameMap.markdown)
}

//兼容旧代码：POST + 流式读取 SSE 文本
export const generateStoryFromCodeStream = async (payload, onMessage) => {
    const result = await analyzeCodeStory(payload)
    onMessage({ type: 'code_story_result', data: result })
    onMessage({ type: 'done' })
}

//需求文档到用户故事：上传 Word / PDF / Markdown / TXT
export const analyzeRequirementDocument = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${BASE_URL}/document_story/analyze`, {
        method: 'POST',
        body: formData
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `需求文档解析失败：${res.status}`)
    }

    return await res.json()
}

//需求文档批量导出
export const exportDocumentStory = async (documentId, format = 'markdown') => {
    const res = await fetch(`${BASE_URL}/document_story/${documentId}/export?format=${format}`)

    if (!res.ok) {
        throw new Error(`导出失败：${res.status}`)
    }

    downloadBlob(await res.blob(), format === 'json' ? '需求文档用户故事.json' : '需求文档用户故事.md')
}

//整个项目源码到用户故事：上传 zip / tar / tar.gz / tgz 项目文件
export const analyzeProjectSource = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${BASE_URL}/project_story/analyze`, {
        method: 'POST',
        body: formData
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `项目源码解析失败：${res.status}`)
    }

    return await res.json()
}


//整个项目源码到用户故事：流式逐节点返回
export const analyzeProjectSourceStream = async (file, onMessage) => {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${BASE_URL}/project_story/analyze_stream`, {
        method: 'POST',
        body: formData
    })

    if (!res.ok || !res.body) {
        const detail = await safeReadError(res)
        throw new Error(detail || `项目源码流式解析失败：${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    // eslint-disable-next-line no-constant-condition
    while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ''
        for (const part of parts) {
            const line = part.split('\n').find(item => item.startsWith('data:'))
            if (!line) continue
            const payload = line.replace(/^data:\s*/, '')
            if (!payload) continue
            await onMessage(JSON.parse(payload))
        }
    }
}

//查询某个函数 / 类节点对应的用户故事
export const getProjectNodeStory = async (projectId, nodeId) => {
    const res = await fetch(`${BASE_URL}/project_story/${projectId}/nodes/${nodeId}`)

    if (!res.ok) {
        throw new Error(`节点用户故事查询失败：${res.status}`)
    }

    return await res.json()
}

//项目源码用户故事批量导出
export const exportProjectStory = async (projectId, format = 'markdown') => {
    const res = await fetch(`${BASE_URL}/project_story/${projectId}/export?format=${format}`)

    if (!res.ok) {
        throw new Error(`导出失败：${res.status}`)
    }

    const filenameMap = {
        json: '项目源码用户故事.json',
        docx: '项目源码用户故事.docx',
        pdf: '项目源码用户故事.pdf',
        markdown: '项目源码用户故事.md',
        md: '项目源码用户故事.md'
    }
    downloadBlob(await res.blob(), filenameMap[format] || filenameMap.markdown)
}

const safeReadError = async (res) => {
    try {
        const data = await res.json()
        return data.detail || data.message || ''
    } catch (error) {
        return ''
    }
}

const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
}

//PDF导出
export const exportPDF = async (payload) => {

    const res = await fetch(`${BASE_URL}/export_pdf`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    const blob = await res.blob()
    downloadBlob(blob, '用户故事报告.pdf')
}

//用户故事优化：上传用户故事文档并逐条优化
export const optimizeUserStoryDocument = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${BASE_URL}/story_optimization/analyze`, {
        method: 'POST',
        body: formData
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `用户故事优化失败：${res.status}`)
    }

    return await res.json()
}

//查询单条用户故事优化详情
export const getUserStoryOptimizationItem = async (optimizationId, storyId) => {
    const res = await fetch(`${BASE_URL}/story_optimization/${optimizationId}/items/${storyId}`)

    if (!res.ok) {
        throw new Error(`用户故事优化详情查询失败：${res.status}`)
    }

    return await res.json()
}

//历史记录：文本 / 代码 / 文档 / 项目源码
export const getStoryHistoryList = async (type, limit = 50) => {
    const res = await fetch(`${BASE_URL}/history/${type}?limit=${limit}`)
    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `历史列表读取失败：${res.status}`)
    }
    return await res.json()
}

export const getStoryHistoryDetail = async (type, id) => {
    const res = await fetch(`${BASE_URL}/history/${type}/${id}`)
    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `历史详情读取失败：${res.status}`)
    }
    return await res.json()
}


//用户故事优化文档导出
export const exportUserStoryOptimization = async (optimizationId, format = 'markdown') => {
    const res = await fetch(`${BASE_URL}/story_optimization/${optimizationId}/export?format=${format}`)

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `优化文档导出失败：${res.status}`)
    }

    const filenameMap = {
        json: '用户故事优化结果.json',
        docx: '用户故事优化结果.docx',
        markdown: '用户故事优化结果.md'
    }

    downloadBlob(await res.blob(), filenameMap[format] || filenameMap.markdown)
}

//智能体配置：展示作用、读取提示词、保存提示词
export const getAgentConfigs = async () => {
    const res = await fetch(`${BASE_URL}/agents/config`)
    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `智能体配置读取失败：${res.status}`)
    }
    return await res.json()
}

export const updateAgentConfig = async (agentId, payload) => {
    const res = await fetch(`${BASE_URL}/agents/config/${agentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `智能体配置保存失败：${res.status}`)
    }

    return await res.json()
}

export const resetAgentConfig = async (agentId) => {
    const res = await fetch(`${BASE_URL}/agents/config/${agentId}/reset`, {
        method: 'POST'
    })

    if (!res.ok) {
        const detail = await safeReadError(res)
        throw new Error(detail || `智能体配置恢复失败：${res.status}`)
    }

    return await res.json()
}
