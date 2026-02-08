<template>
  <div class="designer-wrapper">
    <!-- 工具栏 -->
    <!-- 工具栏 -->
    <div class="designer-toolbar">
      <!-- 内部工具栏已隐藏/移除，由外部控制 -->
    </div>

    <div class="designer-container">
      <div id="lr_workflow_container" class="lr-workflow-container">
        <!-- 原生 JS 将在此处渲染内容 -->
      </div>

      <!-- 属性面板 -->
      <PropertyPanel ref="propertyPanelRef" />

      <!-- 连线配置对话框 -->
      <LinePropertyDialog ref="linePropertyDialogRef" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PropertyPanel from './PropertyPanel.vue'
import LinePropertyDialog from './LinePropertyDialog.vue'

// 引入 CSS
import '../../assets/lr-workflow-ui.css'

// 定义 Props 和 Emits
interface Props {
  initContent?: any // 初始流程内容 (JSON对象)
  readOnly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initContent: null,
  readOnly: false
})

// 定义事件
const emit = defineEmits<{
  nodeClick: [node: any]
  nodeDoubleClick: [node: any]
}>()

const propertyPanelRef = ref()
const linePropertyDialogRef = ref()
const route = useRoute()
const isLoading = ref(false)
const isInitialized = ref(false)  // 标记是否已初始化

// 加载流程数据到设计器
const loadData = (data: any) => {
  const $ = (window as any).$
  if (!$) {
    console.error('jQuery 未加载，无法加载流程数据')
    return false
  }

  const container = $('#lr_workflow_container')
  if (container.length === 0) {
    console.error('设计器容器未找到')
    return false
  }

  try {
    // 确保数据格式正确
    const safeData = data || { nodes: [], lines: [] }

    // 调用 jQuery 插件的 set 方法加载数据
    if ($.fn.lrworkflowSet) {
      container.lrworkflowSet('set', { data: safeData })
    } else {
      console.warn('lrworkflowSet 方法不存在，尝试重新初始化')
      initWorkflow(safeData)
    }
    return true
  } catch (e) {
    console.error('加载流程数据失败', e)
    return false
  }
}

// 获取流程数据
const getData = () => {
  const $ = (window as any).$
  if (!$) {
    console.error('jQuery 未加载')
    return null
  }

  const container = $('#lr_workflow_container')
  if (container.length === 0) {
    console.error('设计器容器未找到')
    return null
  }

  try {
    let content = null

    // 尝试多种方式获取数据
    if ($.fn.lrworkflowGet) {
      content = container.lrworkflowGet()
    } else if (container[0].dfop) {
      content = {
        nodes: container[0].dfop.node || [],
        lines: container[0].dfop.line || []
      }
    } else {
      console.warn('无法获取流程数据')
    }

    return content
  } catch (e) {
    console.error('获取流程数据失败', e)
    return null
  }
}

// 暴露方法给父组件
defineExpose({
  getData,
  loadData
})

// 监听 initContent 变化（移除 deep: true 避免无限循环）
watch(() => props.initContent, (newVal) => {
  if (newVal && isInitialized.value) {
    // 已初始化，只需加载数据
    const $ = (window as any).$
    if ($ && $.lrworkflow) {
      nextTick(() => {
        console.log('监听到 initContent 变化，加载数据:', newVal)
        loadData(newVal)
      })
    }
  }
})

const initLegacyScripts = async () => {
  if (isLoading.value) {
    console.log('正在加载中，跳过重复初始化')
    return
  }

  isLoading.value = true

  try {
    // 1. 手动将 jQuery 暴露给 window
    if (!(window as any).$) {
      const jqueryModule = await import('../../assets/jquery-3.6.0.min.js?raw')
      const script = document.createElement('script')
      script.textContent = jqueryModule.default
      document.head.appendChild(script)
    }

    if (!(window as any).$) {
      console.error('jQuery 加载失败')
      return
    }

    // 2. 初始化 learun 全局对象（必须在加载 lr-workflow-ui.js 之前）
    if (!(window as any).learun) {
      (window as any).learun = {
        newGuid: () => {
          let guid = "";
          for (let i = 1; i <= 32; i++) {
            var n = Math.floor(Math.random() * 16.0).toString(16);
            guid += n;
            if ((i == 8) || (i == 12) || (i == 16) || (i == 20)) guid += "-";
          }
          return guid;
        },
        alert: {
          error: (msg: string) => ElMessage.error(msg),
          success: (msg: string) => ElMessage.success(msg),
          warning: (msg: string) => ElMessage.warning(msg)
        }
      };
    }

    // 3. 加载 lr-workflow-ui.js
    if (!(window as any).$.lrworkflow) {
      const workflowModule = await import('../../assets/lr-workflow-ui.js?raw')
      const script2 = document.createElement('script')
      script2.textContent = workflowModule.default
      document.head.appendChild(script2)
    }

    // 4. 初始化
    initWorkflow(props.initContent)
    isInitialized.value = true

  } catch (e) {
    console.error('加载遗留脚本失败', e)
  } finally {
    isLoading.value = false
  }
}

const initWorkflow = (content: any = null) => {
  const $ = (window as any).$

  const container = $('#lr_workflow_container')
  if (container.length === 0) return

  // 构造 content 对象: 兼容 nodes/node 和 lines/line 两种格式
  const safeContent = content || {}
  const nodes = safeContent.nodes || safeContent.node || []
  const lines = safeContent.lines || safeContent.line || []

  container[0].dfop = {
    id: 'lr_workflow_container',  // 必须与容器的 DOM id 一致
    isPreview: props.readOnly,
    node: [],  // 初始为空，稍后通过 lrworkflowSet 加载
    line: [],  // 初始为空，稍后通过 lrworkflowSet 加载
    nodeRemarks: {
      cursor: '选择',
      direct: '连线',
      startround: '开始节点',
      endround: '结束节点',
      stepnode: '审核节点',
      confluencenode: '会签节点',
      conditionnode: '条件节点',
      auditornode: '传阅节点',
      childwfnode: '子流程节点'
    },
    toolBtns: props.readOnly ? [] : ['startround', 'stepnode', 'confluencenode', 'conditionnode', 'auditornode', 'endround'],
    hasStartround: false,
    hasEndround: false,
    openNode: (nodeData: any, allNodes: any[]) => {
      console.log('打开节点', nodeData, '只读模式:', props.readOnly)

      // 触发节点双击事件（无论是否只读模式）
      emit('nodeDoubleClick', nodeData)

      // 打开属性面板（只读模式下传递 readonly 参数）
      if (propertyPanelRef.value) {
        propertyPanelRef.value.open(nodeData, {
          updateNodeText: (nodeId: string, newText: string) => {
            if ($.fn.lrworkflowSet) {
              container.lrworkflowSet('updateNodeName', { nodeId: nodeId })
            } else if ($.lrworkflow && $.lrworkflow.updateNodeName) {
              $.lrworkflow.updateNodeName(container.find('.lr-workflow-workinner'), nodeId)
            }
          }
        }, props.readOnly)
      }
    },
    openLine: (lineData: any, fromNode: any) => {
      if (props.readOnly) return

      console.log('打开连线配置', lineData, fromNode)

      // 获取所有节点数据
      const allNodes = container[0].dfop.node || []

      // 打开连线配置对话框
      if (linePropertyDialogRef.value) {
        linePropertyDialogRef.value.open(lineData, fromNode, allNodes, (lineId: string) => {
          // 更新连线显示
          if ($.lrworkflow && $.lrworkflow.updateLineName) {
            $.lrworkflow.updateLineName(container, lineId)
          }
        })
      }
    }
  }

  container.html('')

  if ($.lrworkflow && $.lrworkflow.render) {
    $.lrworkflow.render(container)

    // 渲染完成后，如果有数据则加载
    if (nodes.length > 0 || lines.length > 0) {
      // 延迟加载数据，确保 DOM 已经渲染
      setTimeout(() => {
        if ($.fn.lrworkflowSet) {
          container.lrworkflowSet('set', { data: { nodes, lines } })
        }
      }, 100)
    }
  }
}

onMounted(() => {
  initLegacyScripts()
})
</script>

<style scoped>
.designer-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.designer-toolbar {
  display: none;
  /* Hide internal toolbar as it's controlled externally */
}

.designer-container {
  flex: 1;
  width: 100%;
  position: relative;
  overflow: hidden;
  background: white;
  min-height: 500px;
}

.lr-workflow-container {
  height: 100%;
  width: 100%;
  position: relative;
  overflow: hidden;
}
</style>
