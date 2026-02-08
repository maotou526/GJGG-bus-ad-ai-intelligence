<!--
 * @Description: ArcGIS地图组件
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-14 14:46:07
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-21 14:34:34
-->
<template>
  <div 
    class="arcgis-map-wrapper"
    :class="{ 'dark-mode': currentMapStyle === 'dark' }">
    <div ref="mapContainer" class="arcgis-map-container"></div>
    
    <!-- 地图风格切换按钮 -->
    <div class="map-style-switcher">
      <button 
        @click="switchMapStyle('normal')"
        :class="['style-btn', { 'active': currentMapStyle === 'normal' }]">
        ☀️ 常规
      </button>
      <button 
        @click="switchMapStyle('dark')"
        :class="['style-btn', { 'active': currentMapStyle === 'dark' }]">
        🌙 暗黑
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { createMapUtils, type ArcGISMapUtils } from './utils'

// 定义事件
const emit = defineEmits<{
  'map-loaded': []
  'map-error': [error: any]
}>()

// 地图相关类型定义
interface MapLayer {
  url: string
  name: string
  visible?: boolean
  opacity?: number
}

interface MapConfig {
  layers: MapLayer[]
  username: string
  password: string
  tokenUrl: string
}

interface TokenResponse {
  data: string
}

// 组件属性
interface Props {
  width?: string
  height?: string
  config?: Partial<MapConfig>
  maxZoom?: number  // 最大缩放级别
  minZoom?: number  // 最小缩放级别
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '640px',
  config: () => ({}),
  maxZoom: 15,  // 默认最大缩放级别
  minZoom: 10  // 默认不限制最小缩放级别
})

// 当前地图风格
const currentMapStyle = ref<'normal' | 'dark'>('normal')

// 常规风格图层配置
const normalLayersConfig: MapLayer[] = [
  {
    url: 'http://58.211.58.103:8089/KMap/rest/services/tcsl_new/MapServer',
    name: '太仓市基础地图',
    visible: true,
    opacity: 1.0
  },
  {
    url: 'http://58.211.58.103:8089/KMap/rest/services/tcslzj_new/MapServer',
    name: '太仓市点位标识',
    visible: true,
    opacity: 0.8
  },
  {
    url: 'http://58.211.58.103:8089/KMap/rest/services/tcjj_new/MapServer',
    name: '太仓市区域界限',
    visible: false,
    opacity: 0.8
  }
]

// 暗黑风格图层配置
const darkLayersConfig: MapLayer[] = [
  {
    url: 'http://58.211.58.103:8089/KMap/rest/services/tcsl_dark/MapServer',
    // url: 'http://58.211.58.103:8089/KMap/rest/services/tcsl_blue/MapServer',
    name: '太仓市基础地图（暗黑）',
    visible: true,
    opacity: 1.0
  },
  {
    url: 'http://58.211.58.103:8089/KMap/rest/services/tcslzj_dark/MapServer',
    name: '太仓市点位标识',
    visible: true,
    opacity: 0.8
  },
  {
    url: 'http://58.211.58.103:8089/KMap/rest/services/tcjj_new/MapServer',
    name: '太仓市区域界限',
    visible: false,
    opacity: 0.8
  }
]

// 默认配置
const defaultConfig: MapConfig = {
  layers: normalLayersConfig,
  username: 'bitshare123',
  password: 'bst#JS63638369',
  tokenUrl: 'http://58.211.58.103:8089/Token/RemoteTokenServer'
}

// 合并配置
const mapConfig = { ...defaultConfig, ...props.config }

// 地图容器引用
const mapContainer = ref<HTMLElement>()

// 地图实例
let map: any = null
let resizeTimer: number | null = null
let mapUtils: ArcGISMapUtils | null = null

// 声明全局变量类型
declare global {
  interface Window {
    dojo: any
    esri: any
    dijit: any
    $: any
    hex_md5: (str: string) => string
  }
}

/**
 * 加载外部脚本
 * @param src 脚本地址
 * @returns Promise
 */
const loadScript = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 检查脚本是否已加载
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.src = src
    script.onload = () => resolve()
    script.onerror = () => reject(new Error(`Failed to load script: ${src}`))
    document.head.appendChild(script)
  })
}

/**
 * 加载外部样式
 * @param href 样式地址
 * @returns Promise
 */
const loadStyle = (href: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 检查样式是否已加载
    if (document.querySelector(`link[href="${href}"]`)) {
      resolve()
      return
    }

    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = href
    link.onload = () => resolve()
    link.onerror = () => reject(new Error(`Failed to load style: ${href}`))
    document.head.appendChild(link)
  })
}

/**
 * 初始化地图，并将token应用于安全服务
 * @param token 获取到的token
 */
const initMap = (token: string): void => {
  if (!mapContainer.value) {
    console.error('地图容器未找到')
    return
  }

  try {
    console.log('初始化地图，图层数量:', mapConfig.layers.length)

    // 创建地图实例配置对象
    const mapOptions: any = {
      slider: false,  // 隐藏缩放滑块（+和-按钮）
      showAttribution: false,  // 隐藏版权信息
      maxZoom: props.maxZoom  // 设置最大缩放级别
    }
    
    // 如果设置了最小缩放级别，则添加到配置中
    if (props.minZoom !== undefined) {
      mapOptions.minZoom = props.minZoom
    }

    // 创建地图实例，隐藏缩放控件
    map = new window.esri.Map(mapContainer.value, mapOptions)

    // 添加多个图层
    mapConfig.layers.forEach((layerConfig, index) => {
      if (layerConfig.visible !== false) {
        const layerUrl = `${layerConfig.url}?token=${token}`
        console.log(`添加图层 ${index + 1}: ${layerConfig.name}`, layerUrl)

        const layer = new window.esri.layers.ArcGISTiledMapServiceLayer(layerUrl)

        // 设置图层属性
        if (layerConfig.opacity !== undefined) {
          layer.setOpacity(layerConfig.opacity)
        }

        // 设置图层ID用于后续操作
        layer.id = `layer_${index}`

        map.addLayer(layer)
      }
    })

    // 处理地图resize事件
    window.dojo.connect(map, 'onLoad', (theMap: any) => {
      console.log('✅ 地图onLoad事件触发')
      
      // 触发地图加载完成事件
      emit('map-loaded')
      
      window.dojo.connect(window.dijit.byId(mapContainer.value?.id), 'resize', () => {
        if (resizeTimer) {
          clearTimeout(resizeTimer)
        }
        resizeTimer = window.setTimeout(() => {
          map.resize()
          map.reposition()
        }, 500)
      })
    })

    // 添加地图点击事件
    window.dojo.connect(map, 'onClick', (evt: any) => {
      const point = evt.mapPoint
      const longitude = point.x
      const latitude = point.y

      console.log('地图点击坐标:', [longitude, latitude])

      // 触发自定义事件，传递坐标信息
      // const clickEvent = new CustomEvent('map-click', {
      //   detail: {
      //     longitude,
      //     latitude,
      //     point: point,
      //     screenPoint: evt.screenPoint
      //   }
      // })

      // // 向父组件发送事件
      // if (mapContainer.value) {
      //   mapContainer.value.dispatchEvent(clickEvent)
      // }
    })

    console.log('多图层地图初始化完成')

    // 创建地图工具实例
    mapUtils = createMapUtils(map, window.esri, window.dojo)
    console.log('地图工具实例创建成功')

  } catch (error) {
    console.error('地图初始化失败:', error)
    emit('map-error', error)
  }
}

/**
 * 绘制飞线
 */
const drawFlightLine = () => {
  if (!mapUtils) {
    console.warn('地图工具未初始化')
    return
  }

  try {
    // 使用工具类绘制飞线
    mapUtils.drawFlightLine({
      startPoint: [121.07969741821289, 31.523986053466793],
      endPoint: [121.17067794799804, 31.58647079467773],
      startColor: [0, 255, 0, 0.8],   // 绿色
      endColor: [255, 0, 0, 0.8],     // 红色
      lineColor: [0, 0, 255, 0.8],    // 蓝色
      lineWidth: 5,
      markerSize: 20,
      layerId: 'flightLineLayer',
      onClick: (graphic: any) => {
        console.log('飞线点击事件:', graphic)
        if (graphic.attributes) {
          alert(`点击了: ${graphic.attributes.name}`)
        }
      }
    })

    // 缩放到飞线范围
    mapUtils.zoomToExtent([
      Math.min(121.07969741821289, 121.17067794799804) - 0.01,
      Math.min(31.523986053466793, 31.58647079467773) - 0.01,
      Math.max(121.07969741821289, 121.17067794799804) + 0.01,
      Math.max(31.523986053466793, 31.58647079467773) + 0.01
    ])
  } catch (error: any) {
    console.error('绘制飞线失败:', error)
  }
}

/**
 * 绘制测试长方形
 */
const drawTestRectangle = () => {
  if (!mapUtils) {
    console.warn('地图工具未初始化')
    return
  }

  // 先检查图层的空间参考信息
  // checkLayerSpatialReference() // 暂时注释掉，这个函数可能未定义

  try {
    // 使用工具类绘制矩形
    mapUtils.drawRectangle({
      bottomLeft: [121.07969741821289, 31.523986053466793],
      topRight: [121.17067794799804, 31.58647079467773],
      fillColor: [255, 0, 0, 0.5],     // 红色半透明
      outlineColor: [255, 255, 0, 1],  // 黄色边框
      outlineWidth: 5,
      layerId: 'testRectangleLayer',
      attributes: {
        id: 'test_rectangle',
        name: '测试长方形'
      },
      onClick: (graphic: any) => {
        console.log('矩形点击事件:', graphic)
        if (graphic.attributes) {
          alert(`点击了: ${graphic.attributes.name}`)
        }
      }
    })
  } catch (error: any) {
    console.error('绘制测试长方形失败:', error)
  }
}

// 当前 token（用于图层切换）
let currentToken: string = ''

/**
 * 获取token
 */
const fetchToken = async (): Promise<void> => {
  try {
    const username = mapConfig.username
    const password = mapConfig.password
    const hashedPassword = window.hex_md5(password).toUpperCase()
    const tokenUrl = `${mapConfig.tokenUrl}?UserName=${username}&PwdMD5=${hashedPassword}`

    console.log('正在获取token...')

    const response = await window.$.ajax({
      type: 'GET',
      contentType: 'application/json',
      url: tokenUrl
    })

    if (response && response.data) {
      console.log('Token获取成功')
      currentToken = response.data
      initMap(response.data)
    } else {
      console.error('Token获取失败: 响应数据无效')
    }
  } catch (error) {
    console.error('Token获取失败:', error)
    emit('map-error', error)
  }
}

/**
 * 切换地图风格
 * @param style 地图风格：'normal' | 'dark'
 */
const switchMapStyle = (style: 'normal' | 'dark'): void => {
  if (!map || !currentToken) {
    console.warn('地图未初始化或token不存在')
    return
  }
  
  if (currentMapStyle.value === style) {
    console.log('已经是当前风格，无需切换')
    return
  }
  
  console.log(`切换地图风格: ${currentMapStyle.value} → ${style}`)
  
  try {
    // 移除所有现有图层
    const layerIds = map.layerIds.slice() // 复制数组，避免遍历时修改
    layerIds.forEach((layerId: string) => {
      const layer = map.getLayer(layerId)
      if (layer) {
        map.removeLayer(layer)
        console.log(`移除图层: ${layerId}`)
      }
    })
    
    // 选择新的图层配置
    const newLayers = style === 'dark' ? darkLayersConfig : normalLayersConfig
    
    // 添加新的图层
    newLayers.forEach((layerConfig, index) => {
      if (layerConfig.visible !== false) {
        const layerUrl = `${layerConfig.url}?token=${currentToken}`
        console.log(`添加图层 ${index + 1}: ${layerConfig.name}`, layerUrl)

        const layer = new window.esri.layers.ArcGISTiledMapServiceLayer(layerUrl)

        // 设置图层属性
        if (layerConfig.opacity !== undefined) {
          layer.setOpacity(layerConfig.opacity)
        }

        // 设置图层ID用于后续操作
        layer.id = `layer_${index}`

        map.addLayer(layer)
      }
    })
    
    // 更新当前风格
    currentMapStyle.value = style
    console.log(`✅ 地图风格切换完成: ${style}`)
    
  } catch (error) {
    console.error('❌ 切换地图风格失败:', error)
  }
}

/**
 * 初始化所有依赖
 * 注意：CSS和JS已在index.html中预加载，这里只需等待dojo初始化完成
 */
const initializeDependencies = async (): Promise<void> => {
  try {
    console.log('等待 ArcGIS API 初始化...')
    
    // 等待dojo和esri加载完成
    await new Promise<void>((resolve, reject) => {
      let checkCount = 0
      const maxChecks = 100 // 最多检查10秒（100 * 100ms）
      
      const checkLibraries = () => {
        checkCount++
        
        // 检查必要的全局对象是否已加载
        if (window.dojo && window.esri && window.$) {
          console.log('✅ ArcGIS API 全局对象已加载')
          
          // 加载必要的dojo模块
          try {
            window.dojo.require('dijit.layout.BorderContainer')
            window.dojo.require('dijit.layout.ContentPane')
            window.dojo.require('esri.map')
            console.log('✅ Dojo模块加载完成')
            resolve()
          } catch (error) {
            console.error('❌ Dojo模块加载失败:', error)
            reject(error)
          }
        } else if (checkCount >= maxChecks) {
          const missing = []
          if (!window.dojo) missing.push('dojo')
          if (!window.esri) missing.push('esri')
          if (!window.$) missing.push('jQuery')
          
          const error = new Error(`ArcGIS API 加载超时，缺少: ${missing.join(', ')}`)
          console.error('❌', error.message)
          reject(error)
        } else {
          // 继续等待
          setTimeout(checkLibraries, 100)
        }
      }
      
      checkLibraries()
    })

    console.log('✅ 所有依赖初始化完成')
  } catch (error) {
    console.error('❌ 依赖初始化失败:', error)
    emit('map-error', error)
    throw error
  }
}

// 组件挂载时初始化
onMounted(async () => {
  await nextTick()
  await initializeDependencies()
  await fetchToken()
})

// 组件卸载时清理
onUnmounted(() => {
  if (resizeTimer) {
    clearTimeout(resizeTimer)
  }
  if (map) {
    map.destroy()
    map = null
  }
})

/**
 * 控制图层显示/隐藏
 * @param layerIndex 图层索引
 * @param visible 是否显示
 */
const toggleLayerVisibility = (layerIndex: number, visible: boolean): void => {
  if (!map) {
    console.warn('地图未初始化')
    return
  }

  const layer = map.getLayer(`layer_${layerIndex}`)
  if (layer) {
    layer.setVisibility(visible)
    console.log(`图层 ${layerIndex} 可见性设置为:`, visible)
  }
}

/**
 * 设置图层透明度
 * @param layerIndex 图层索引
 * @param opacity 透明度 (0-1)
 */
const setLayerOpacity = (layerIndex: number, opacity: number): void => {
  if (!map) {
    console.warn('地图未初始化')
    return
  }

  const layer = map.getLayer(`layer_${layerIndex}`)
  if (layer) {
    layer.setOpacity(opacity)
    console.log(`图层 ${layerIndex} 透明度设置为:`, opacity)
  }
}

/**
 * 获取所有图层信息
 */
const getLayersInfo = () => {
  if (!map) {
    return []
  }

  return mapConfig.layers.map((layerConfig, index) => {
    const layer = map.getLayer(`layer_${index}`)
    return {
      index,
      name: layerConfig.name,
      url: layerConfig.url,
      visible: layer ? layer.visible : layerConfig.visible,
      opacity: layer ? layer.opacity : layerConfig.opacity
    }
  })
}

/**
 * 注入方法，允许外部组件传入回调函数来操作地图
 * @param callback 回调函数，参数为地图实例
 */
const injectMethod = (callback: (map: any) => void): void => {
  if (typeof callback === 'function') {
    callback(map)
  } else {
    console.warn('injectMethod: 参数必须是函数类型')
  }
}

// 暴露方法给父组件
defineExpose({
  getMap: () => map,
  getMapUtils: () => mapUtils,
  refresh: fetchToken,
  toggleLayerVisibility,
  setLayerOpacity,
  getLayersInfo,
  injectMethod,
  switchMapStyle,
  getCurrentMapStyle: () => currentMapStyle.value
})
</script>

<style scoped>
.arcgis-map-wrapper {
  position: relative;
  width: v-bind(width);
  height: v-bind(height);
  transition: background-color 0.3s ease;
}

/* 暗黑模式背景 */
.arcgis-map-wrapper.dark-mode {
  background: #1f3946;
}

.arcgis-map-container {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  border: 0;
}

/* 确保地图容器有正确的尺寸 */
.arcgis-map-container :deep(#map) {
  width: 100% !important;
  height: 100% !important;
}

/* 地图风格切换按钮 */
.map-style-switcher {
  position: absolute;
  bottom: 10px;
  left: 20px;
  z-index: 1000;
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 6px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transition: background-color 0.3s ease;
}

/* 暗黑模式下的按钮容器 */
.dark-mode .map-style-switcher {
  background: rgba(31, 57, 70, 0.95);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.style-btn {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.style-btn:hover {
  color: #409eff;
  border-color: #409eff;
  background: #ecf5ff;
}

.style-btn.active {
  color: white;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.style-btn:active {
  transform: scale(0.98);
}

/* 暗黑模式下的按钮样式 */
.dark-mode .style-btn {
  color: #c0c4cc;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.dark-mode .style-btn:hover {
  color: #66b1ff;
  border-color: #66b1ff;
  background: rgba(102, 177, 255, 0.1);
}

.dark-mode .style-btn.active {
  color: white;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
}
</style>
