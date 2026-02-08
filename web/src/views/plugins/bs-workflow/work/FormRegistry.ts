import { defineAsyncComponent, type Component } from 'vue'

/**
 * 工作流表单动态加载器
 *
 * 表单路径约定：
 * - 配置格式：basedata/roadline/RoadlineForm (相对于 /src/views/ 的路径)
 * - 对应实际文件路径：/src/views/basedata/roadline/RoadlineForm/index.vue
 *
 * 使用 import.meta.glob 实现动态加载，无需手动注册
 */

// 使用 import.meta.glob 获取所有可能的表单组件
// 匹配规则：views 下所有包含 Form 的文件夹中的 index.vue
const formModules = import.meta.glob([
    '/src/views/**/index.vue',
    '/src/views/**/*Form.vue',
    '/src/views/**/*Form/index.vue',
    // '/src/views/**/components/**/*.vue' // 支持 components 目录下的组件
])

// 白名单路径的单独 glob（精确匹配特定文件）
const whitelistFormModules = import.meta.glob([
    '/src/views/booking_manage/booking_order/BookingOrderModelViewSet/components/BookingOrderReviewPage.vue'
], { eager: false })

// 无默认表单，找不到时返回 null

// 缓存已加载的组件
const componentCache: Record<string, Component> = {}

// 表单路径白名单映射（用于特殊路径的映射）
// key: 相对路径（相对于 /src/views/，不包含 .vue 后缀），value: 完整路径（相对于 /src/views/，包含 .vue 后缀）
const formPathWhitelist: Record<string, string> = {
    'booking_manage/booking_order/BookingOrderModelViewSet/components/BookingOrderReviewPage': 
        'booking_manage/booking_order/BookingOrderModelViewSet/components/BookingOrderReviewPage.vue'
}

/**
 * 解析表单URL，分离路径和查询参数
 * 例如：basedata/roadline/RoadlineForm?viewFlag=1&readonly=true
 * 返回：{ path: 'basedata/roadline/RoadlineForm', params: { viewFlag: '1', readonly: 'true' } }
 * @param url 带参数的URL
 * @returns 路径和参数对象
 */
export function parseFormUrl(url: string): {
    path: string
    params: Record<string, string>
} {
    if (!url) return { path: '', params: {} }

    const [pathPart, queryPart] = url.split('?')
    const params: Record<string, string> = {}

    if (queryPart) {
        const searchParams = new URLSearchParams(queryPart)
        searchParams.forEach((value, key) => {
            params[key] = value
        })
    }

    return {
        path: normalizeFormPath(pathPart),
        params
    }
}

/**
 * 标准化表单路径
 * - 移除开头的斜杠
 * - 移除 /src/views/ 前缀（如果有）
 * @param url 原始路径
 * @returns 标准化后的相对路径
 */
export function normalizeFormPath(url: string): string {
    if (!url) return ''

    let path = url

    // 移除开头的斜杠
    if (path.startsWith('/')) {
        path = path.slice(1)
    }

    // 移除 src/views/ 前缀（如果有）
    if (path.startsWith('src/views/')) {
        path = path.slice('src/views/'.length)
    }

    return path
}

/**
 * 根据路径动态加载表单组件
 * @param formPath 表单路径（如 'basedata/roadline/RoadlineForm'）
 * @returns 异步组件
 */
export function getFormByPath(formPath: string): Component | null {
    if (!formPath) return null

    // 标准化路径：移除 .vue 后缀（如果存在）
    const normalizedPath = formPath.endsWith('.vue') ? formPath.slice(0, -4) : formPath

    // 如果已缓存，直接返回
    if (componentCache[normalizedPath]) {
        return componentCache[normalizedPath]
    }

    // 1. 优先检查白名单映射（支持带或不带 .vue 后缀的路径）
    const whitelistKey = normalizedPath
    if (formPathWhitelist[whitelistKey]) {
        const whitelistRelativePath = formPathWhitelist[whitelistKey]
        const fullPath = `/src/views/${whitelistRelativePath}`
        // 从白名单专用的 glob 中查找
        if (whitelistFormModules[fullPath]) {
            const component = defineAsyncComponent(whitelistFormModules[fullPath] as any)
            componentCache[normalizedPath] = component
            return component
        }
    }

    // 2. 尝试多种路径格式匹配
    const possiblePaths = [
        `/src/views/${normalizedPath}/index.vue`,
        `/src/views/${normalizedPath}.vue`,
        `/src/views/${normalizedPath}Form/index.vue`,
        `/src/views/${normalizedPath}Form.vue`
    ]

    for (const path of possiblePaths) {
        if (formModules[path]) {
            const component = defineAsyncComponent(formModules[path] as any)
            componentCache[normalizedPath] = component
            return component
        }
    }

    console.warn(`[FormRegistry] 未找到表单组件: ${formPath}`)
    return null
}

/**
 * 根据流程编码获取默认表单
 * 这是一个兼容方法，实际应该从 scheme.content 的节点配置中获取表单
 * @param schemeCode 流程模板编码
 */
export function getFormBySchemeCode(schemeCode: string): Component | null {
    // 流程编码到表单路径的映射（可选的快捷映射）
    const schemeFormMap: Record<string, string> = {
        'ROADLINE_FLOW': 'basedata/roadline/RoadlineForm',
        'test01': 'basedata/roadline/RoadlineForm'
    }

    const formPath = schemeFormMap[schemeCode]
    if (formPath) {
        const form = getFormByPath(formPath)
        if (form) return form
    }

    // 未找到表单
    return null
}

/**
 * 从节点配置中获取表单组件
 * @param nodeConfig 节点配置（包含 wfForms 数组）
 * @param formType 表单类型：'0' = 系统表单, '1' = 自定义表单
 * @returns 表单组件
 */
export function getFormByNodeConfig(nodeConfig: any, formType: string = '0'): Component | null {
    if (!nodeConfig?.wfForms || !Array.isArray(nodeConfig.wfForms)) {
        return null
    }

    // 查找指定类型的表单
    const formConfig = nodeConfig.wfForms.find((f: any) => f.formType === formType || f.type === formType)

    // 获取URL（可能是 formUrl 或 url）
    const url = formConfig?.formUrl || formConfig?.url
    if (!url) {
        return null
    }

    // 解析URL，分离路径和参数
    const { path } = parseFormUrl(url)
    return getFormByPath(path)
}

/**
 * 从节点配置中获取表单相关信息
 * @param nodeConfig 节点配置
 * @param formType 表单类型
 * @returns 包含表单组件、路径和参数信息
 */
export function getFormInfo(nodeConfig: any, formType: string = '0'): {
    component: Component | null
    formPath: string
    params: Record<string, string>
    originalUrl: string
} {
    const result = {
        component: null as Component | null,
        formPath: '',
        params: {} as Record<string, string>,
        originalUrl: ''
    }

    if (!nodeConfig?.wfForms || !Array.isArray(nodeConfig.wfForms)) {
        return result
    }

    // 查找指定类型的表单
    const formConfig = nodeConfig.wfForms.find((f: any) => f.formType === formType || f.type === formType)
    const url = formConfig?.formUrl || formConfig?.url
    if (!url) {
        return result
    }

    result.originalUrl = url
    // 解析URL，分离路径和参数
    const { path, params } = parseFormUrl(url)
    result.formPath = path
    result.params = params
    result.component = getFormByPath(path)

    return result
}

/**
 * 智能获取表单组件
 * 1. 优先从节点配置获取
 * 2. 其次按路径查找
 * 3. 最后按流程编码查找
 * @param options 配置选项
 */
export function getForm(options: {
    nodeConfig?: any
    formPath?: string
    schemeCode?: string
    formType?: string
}): Component | null {
    const { nodeConfig, formPath, schemeCode, formType = '0' } = options

    // 1. 从节点配置获取
    if (nodeConfig) {
        const form = getFormByNodeConfig(nodeConfig, formType)
        if (form) return form
    }

    // 2. 按路径获取
    if (formPath) {
        const form = getFormByPath(formPath)
        if (form) return form
    }

    // 3. 按流程编码获取
    if (schemeCode) {
        return getFormBySchemeCode(schemeCode)
    }

    // 未找到表单
    return null
}

// 默认导出
export default {
    getForm,
    getFormByPath,
    getFormBySchemeCode,
    getFormByNodeConfig,
    getFormInfo,
    parseFormUrl,
    normalizeFormPath
}
