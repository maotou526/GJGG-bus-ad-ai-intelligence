/**
 * ArcGIS 地图工具类
 * 提供飞线、矩形等图形绘制功能
 */

/**
 * 点坐标类型
 */
export interface PointCoord {
  x: number
  y: number
}

/**
 * 飞线配置
 */
export interface FlightLineConfig {
  startPoint: [number, number]  // 起点坐标 [经度, 纬度]
  endPoint: [number, number]    // 终点坐标 [经度, 纬度]
  startColor?: [number, number, number, number]  // 起点颜色 RGBA
  endColor?: [number, number, number, number]    // 终点颜色 RGBA
  lineColor?: [number, number, number, number]   // 线条颜色 RGBA
  lineWidth?: number            // 线条宽度
  markerSize?: number           // 标记点大小
  layerId?: string              // 图层ID
  clearIfExists?: boolean       // 图层已存在时是否清空（默认false）
  connectionData?: any          // 连接数据（用于点击时显示详情）
  onClick?: (graphic: any) => void  // 点击回调
}

/**
 * 矩形配置
 */
export interface RectangleConfig {
  bottomLeft: [number, number]  // 左下角坐标 [经度, 纬度]
  topRight: [number, number]    // 右上角坐标 [经度, 纬度]
  fillColor?: [number, number, number, number]    // 填充颜色 RGBA
  outlineColor?: [number, number, number, number] // 边框颜色 RGBA
  outlineWidth?: number         // 边框宽度
  layerId?: string              // 图层ID
  attributes?: Record<string, any>  // 附加属性
  onClick?: (graphic: any) => void  // 点击回调
}

/**
 * 地图工具类
 */
export class ArcGISMapUtils {
  private map: any
  private esri: any
  private dojo: any

  constructor(map: any, esri: any, dojo: any) {
    this.map = map
    this.esri = esri
    this.dojo = dojo
  }

  /**
   * 获取地图的空间参考
   */
  private getMapSpatialReference(): any {
    return this.map?.spatialReference || { wkid: 4490 }
  }

  /**
   * 创建或获取图层
   * @param layerId 图层ID
   * @param title 图层标题
   * @param clearIfExists 如果图层已存在是否清空（默认true）
   */
  private getOrCreateLayer(layerId: string, title?: string, clearIfExists: boolean = true): any {
    // 检查图层是否已存在
    let layer = this.map.getLayer(layerId)
    
    if (layer) {
      // 如果图层已存在，根据参数决定是否清空
      if (clearIfExists && layer.clear) {
        layer.clear()
      }
    } else {
      // 创建新图层
      layer = new this.esri.layers.GraphicsLayer()
      layer.id = layerId
      if (title) {
        layer.title = title
      }
      this.map.addLayer(layer)
      console.log(`✅ 创建新图层: ${layerId}`)
    }
    
    return layer
  }

  /**
   * 绘制飞线
   * @param config 飞线配置
   * @returns 图层实例
   */
  drawFlightLine(config: FlightLineConfig): any {
    try {
      // console.log('✈️ 开始绘制飞线...')

      // 默认配置
      const {
        startPoint,
        endPoint,
        startColor = [0, 255, 0, 0.8],      // 绿色
        endColor = [255, 0, 0, 0.8],        // 红色
        lineColor = [0, 0, 255, 0.8],       // 蓝色
        lineWidth = 5,
        markerSize = 20,
        layerId = 'flightLineLayer',
        clearIfExists = false,              // 默认不清空图层
        connectionData,                     // 连接数据
        onClick
      } = config

      // 获取或创建图层
      const flightLayer = this.getOrCreateLayer(layerId, '飞线图层', clearIfExists)

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()

      // 创建起点
      const startGeometry = new this.esri.geometry.Point(startPoint[0], startPoint[1], mapSR)

      // 创建终点
      const endGeometry = new this.esri.geometry.Point(endPoint[0], endPoint[1], mapSR)

      // 创建起点符号
      const startSymbol = new this.esri.symbol.SimpleMarkerSymbol(
        this.esri.symbol.SimpleMarkerSymbol.STYLE_CIRCLE,
        markerSize,
        new this.esri.symbol.SimpleLineSymbol(
          this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
          new this.dojo.Color([255, 255, 255]),
          2
        ),
        new this.dojo.Color(startColor)
      )

      // 创建终点符号
      const endSymbol = new this.esri.symbol.SimpleMarkerSymbol(
        this.esri.symbol.SimpleMarkerSymbol.STYLE_CIRCLE,
        markerSize,
        new this.esri.symbol.SimpleLineSymbol(
          this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
          new this.dojo.Color([255, 255, 255]),
          2
        ),
        new this.dojo.Color(endColor)
      )

      // 创建飞线符号
      const lineSymbol = new this.esri.symbol.SimpleLineSymbol(
        this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
        new this.dojo.Color(lineColor),
        lineWidth
      )

      // 创建起点图形
      const startGraphic = new this.esri.Graphic(startGeometry, startSymbol, {
        type: 'start',
        name: '起点',
        startPoint,
        endPoint
      })

      // 创建终点图形
      const endGraphic = new this.esri.Graphic(endGeometry, endSymbol, {
        type: 'end',
        name: '终点',
        startPoint,
        endPoint
      })

      // 创建飞线图形（带弧度）
      const polyline = new this.esri.geometry.Polyline(mapSR)
      
      // 生成弧形路径点
      const arcPoints = this.generateArcPath(startPoint, endPoint, 0.3) // 0.3 是弧度系数
      polyline.addPath(arcPoints)

      const lineGraphic = new this.esri.Graphic(polyline, lineSymbol, {
        type: 'flight_line',
        name: '飞线',
        startPoint,
        endPoint,
        connectionData  // 附加连接数据到飞线图形上
      })

      // 添加飞线图形到图层
      flightLayer.add(lineGraphic)
      
      // 只有当 markerSize > 0 时才添加起点和终点标记
      if (markerSize > 0) {
        flightLayer.add(startGraphic)
        flightLayer.add(endGraphic)
      }

      // 添加点击事件
      if (onClick) {
        this.dojo.connect(flightLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      return flightLayer
    } catch (error: any) {
      console.error('绘制飞线失败:', error)
      throw error
    }
  }

  /**
   * 生成弧形路径点（用于绘制弧线）
   * @param startPoint 起点 [经度, 纬度]
   * @param endPoint 终点 [经度, 纬度]
   * @param curvature 弧度系数（0-1之间，值越大弧度越大），默认0.3
   * @returns 弧形路径点数组
   */
  private generateArcPath(
    startPoint: [number, number],
    endPoint: [number, number],
    curvature: number = 0.3
  ): Array<[number, number]> {
    // 计算中点
    const midX = (startPoint[0] + endPoint[0]) / 2
    const midY = (startPoint[1] + endPoint[1]) / 2
    
    // 计算起点到终点的向量
    const dx = endPoint[0] - startPoint[0]
    const dy = endPoint[1] - startPoint[1]
    
    // 计算距离
    const distance = Math.sqrt(dx * dx + dy * dy)
    
    // 计算垂直于连线的控制点偏移
    // 使用垂直向量 (-dy, dx) 来创建弧度
    const offsetX = -dy * curvature
    const offsetY = dx * curvature
    
    // 控制点位置（在中点的垂直方向上偏移）
    const controlX = midX + offsetX
    const controlY = midY + offsetY
    
    // 使用二次贝塞尔曲线生成平滑的弧线
    // 生成50个点来绘制平滑曲线
    const points: Array<[number, number]> = []
    const segments = 50
    
    for (let i = 0; i <= segments; i++) {
      const t = i / segments
      
      // 二次贝塞尔曲线公式：B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
      const x = 
        Math.pow(1 - t, 2) * startPoint[0] +
        2 * (1 - t) * t * controlX +
        Math.pow(t, 2) * endPoint[0]
      
      const y = 
        Math.pow(1 - t, 2) * startPoint[1] +
        2 * (1 - t) * t * controlY +
        Math.pow(t, 2) * endPoint[1]
      
      points.push([x, y])
    }
    
    return points
  }

  /**
   * 绘制矩形
   * @param config 矩形配置
   * @returns 图层实例
   */
  drawRectangle(config: RectangleConfig): any {
    try { 
      // 默认配置
      const {
        bottomLeft,
        topRight,
        fillColor = [255, 0, 0, 0.5],       // 红色半透明
        outlineColor = [255, 255, 0],       // 黄色边框
        outlineWidth = 5,
        layerId = 'rectangleLayer',
        attributes = {},
        onClick
      } = config

      // 获取或创建图层
      const rectangleLayer = this.getOrCreateLayer(layerId, '矩形图层')

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()

      // 创建矩形几何体
      const extent = new this.esri.geometry.Extent(
        bottomLeft[0],
        bottomLeft[1],
        topRight[0],
        topRight[1],
        mapSR
      )

      // 创建矩形符号
      const symbol = new this.esri.symbol.SimpleFillSymbol(
        this.esri.symbol.SimpleFillSymbol.STYLE_SOLID,
        new this.esri.symbol.SimpleLineSymbol(
          this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
          new this.dojo.Color(outlineColor),
          outlineWidth
        ),
        new this.dojo.Color(fillColor)
      )

      // 创建图形
      const graphic = new this.esri.Graphic(extent, symbol, {
        ...attributes,
        bottomLeft,
        topRight
      })

      // 添加到图层
      rectangleLayer.add(graphic)
      // 添加点击事件
      if (onClick) {
        this.dojo.connect(rectangleLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      return rectangleLayer
    } catch (error: any) {
      console.error('绘制矩形失败:', error)
      throw error
    }
  }

  /**
   * 批量绘制矩形
   * @param rectangles 矩形配置数组
   * @param layerId 图层ID
   * @param onClick 点击回调
   * @returns 图层实例
   */
  drawMultipleRectangles(
    rectangles: Array<Omit<RectangleConfig, 'layerId' | 'onClick'>>,
    layerId: string = 'multiRectangleLayer',
    onClick?: (graphic: any) => void
  ): any {
    try {
      console.log(`🗺️ 开始批量绘制矩形，数量: ${rectangles.length}`)

      // 获取或创建图层
      const rectangleLayer = this.getOrCreateLayer(layerId, '批量矩形图层')

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()

      let successCount = 0

      rectangles.forEach((rectConfig, index) => {
        try {
          const {
            bottomLeft,
            topRight,
            fillColor = [255, 0, 0, 0.5],
            outlineColor = [255, 255, 0],
            outlineWidth = 3,
            attributes = {}
          } = rectConfig

          // 创建矩形几何体
          const extent = new this.esri.geometry.Extent(
            bottomLeft[0],
            bottomLeft[1],
            topRight[0],
            topRight[1],
            mapSR
          )

          // 创建矩形符号
          const symbol = new this.esri.symbol.SimpleFillSymbol(
            this.esri.symbol.SimpleFillSymbol.STYLE_SOLID,
            new this.esri.symbol.SimpleLineSymbol(
              this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
              new this.dojo.Color(outlineColor),
              outlineWidth
            ),
            new this.dojo.Color(fillColor)
          )

          // 创建图形
          const graphic = new this.esri.Graphic(extent, symbol, {
            ...attributes,
            index,
            bottomLeft,
            topRight
          })

          rectangleLayer.add(graphic)
          successCount++
        } catch (error) {
          console.error(`绘制第 ${index + 1} 个矩形失败:`, error)
        }
      })

      console.log(`✅ 批量矩形绘制完成，成功: ${successCount}/${rectangles.length}`)

      // 添加点击事件
      if (onClick) {
        this.dojo.connect(rectangleLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      return rectangleLayer
    } catch (error: any) {
      console.error('批量绘制矩形失败:', error)
      throw error
    }
  }

  /**
   * 缩放到指定范围
   * @param extent 范围 [xmin, ymin, xmax, ymax] 或 {xmin, ymin, xmax, ymax}
   * @param animate 是否动画
   */
  zoomToExtent(extent: [number, number, number, number] | {xmin: number, ymin: number, xmax: number, ymax: number}, animate: boolean = true): void {
    try {
      const mapSR = this.getMapSpatialReference()
      let xmin, ymin, xmax, ymax
      
      if (Array.isArray(extent)) {
        [xmin, ymin, xmax, ymax] = extent
      } else {
        ({xmin, ymin, xmax, ymax} = extent)
      }
      
      const mapExtent = new this.esri.geometry.Extent(xmin, ymin, xmax, ymax, mapSR)
      this.map.setExtent(mapExtent, animate)
      console.log('✅ 地图已缩放到指定范围')
    } catch (error) {
      console.error('缩放地图失败:', error)
    }
  }

  /**
   * 自动缩放到指定图层的范围
   * @param layerId 图层ID
   * @param padding 边距比例（0-1），默认0.1表示10%边距
   * @param animate 是否动画
   */
  zoomToLayer(layerId: string, padding: number = 0.1, animate: boolean = true): void {
    try {
      const layer = this.map.getLayer(layerId)
      if (!layer) {
        console.warn(`图层 ${layerId} 不存在`)
        return
      }

      // 获取图层的所有图形
      const graphics = layer.graphics
      if (!graphics || graphics.length === 0) {
        console.warn(`图层 ${layerId} 没有图形，数量: ${graphics ? graphics.length : 0}`)
        return
      }

      console.log(`开始计算图层范围，图形数量: ${graphics.length}`)

      // 手动计算所有图形的边界框
      let minX = Infinity
      let minY = Infinity
      let maxX = -Infinity
      let maxY = -Infinity

      graphics.forEach((graphic: any) => {
        if (graphic.geometry) {
          const geom = graphic.geometry
          
          // 处理不同类型的几何对象
          if (geom.type === 'point') {
            minX = Math.min(minX, geom.x)
            minY = Math.min(minY, geom.y)
            maxX = Math.max(maxX, geom.x)
            maxY = Math.max(maxY, geom.y)
          } else if (geom.type === 'polyline' && geom.paths) {
            geom.paths.forEach((path: any[]) => {
              path.forEach((point: any) => {
                minX = Math.min(minX, point[0])
                minY = Math.min(minY, point[1])
                maxX = Math.max(maxX, point[0])
                maxY = Math.max(maxY, point[1])
              })
            })
          } else if (geom.type === 'polygon' && geom.rings) {
            geom.rings.forEach((ring: any[]) => {
              ring.forEach((point: any) => {
                minX = Math.min(minX, point[0])
                minY = Math.min(minY, point[1])
                maxX = Math.max(maxX, point[0])
                maxY = Math.max(maxY, point[1])
              })
            })
          }
        }
      })

      // 检查是否计算出有效的边界
      if (!isFinite(minX) || !isFinite(minY) || !isFinite(maxX) || !isFinite(maxY)) {
        console.warn('无法计算有效的图形范围')
        return
      }

      console.log(`计算出的范围: [${minX}, ${minY}, ${maxX}, ${maxY}]`)

      // 添加边距
      if (padding > 0) {
        const width = maxX - minX
        const height = maxY - minY
        const xPadding = width * padding
        const yPadding = height * padding

        minX -= xPadding
        minY -= yPadding
        maxX += xPadding
        maxY += yPadding
      }

      // 创建 Extent 对象并缩放
      const mapSR = this.getMapSpatialReference()
      const extent = new this.esri.geometry.Extent(minX, minY, maxX, maxY, mapSR)
      this.map.setExtent(extent, animate)
      console.log(`✅ 地图已自动缩放到图层 ${layerId} 的范围`)
    } catch (error) {
      console.error('缩放到图层范围失败:', error)
    }
  }

  /**
   * 自动缩放到多个图层的范围
   * @param layerIds 图层ID数组
   * @param padding 边距比例（0-1），默认0.1表示10%边距
   * @param animate 是否动画
   */
  zoomToLayers(layerIds: string[], padding: number = 0.1, animate: boolean = true): void {
    try {
      const allGraphics: any[] = []

      // 收集所有图层的图形
      layerIds.forEach(layerId => {
        const layer = this.map.getLayer(layerId)
        if (layer && layer.graphics) {
          allGraphics.push(...layer.graphics)
        }
      })

      if (allGraphics.length === 0) {
        console.warn('没有找到任何图形')
        return
      }

      // 手动计算所有图形的边界框
      let minX = Infinity
      let minY = Infinity
      let maxX = -Infinity
      let maxY = -Infinity

      allGraphics.forEach((graphic: any) => {
        if (graphic.geometry) {
          const geom = graphic.geometry
          
          // 处理不同类型的几何对象
          if (geom.type === 'point') {
            minX = Math.min(minX, geom.x)
            minY = Math.min(minY, geom.y)
            maxX = Math.max(maxX, geom.x)
            maxY = Math.max(maxY, geom.y)
          } else if (geom.type === 'polyline' && geom.paths) {
            geom.paths.forEach((path: any[]) => {
              path.forEach((point: any) => {
                minX = Math.min(minX, point[0])
                minY = Math.min(minY, point[1])
                maxX = Math.max(maxX, point[0])
                maxY = Math.max(maxY, point[1])
              })
            })
          } else if (geom.type === 'polygon' && geom.rings) {
            geom.rings.forEach((ring: any[]) => {
              ring.forEach((point: any) => {
                minX = Math.min(minX, point[0])
                minY = Math.min(minY, point[1])
                maxX = Math.max(maxX, point[0])
                maxY = Math.max(maxY, point[1])
              })
            })
          }
        }
      })

      // 检查是否计算出有效的边界
      if (!isFinite(minX) || !isFinite(minY) || !isFinite(maxX) || !isFinite(maxY)) {
        console.warn('无法计算有效的图形范围')
        return
      }

      // 添加边距
      if (padding > 0) {
        const width = maxX - minX
        const height = maxY - minY
        const xPadding = width * padding
        const yPadding = height * padding

        minX -= xPadding
        minY -= yPadding
        maxX += xPadding
        maxY += yPadding
      }

      // 创建 Extent 对象并缩放
      const mapSR = this.getMapSpatialReference()
      const extent = new this.esri.geometry.Extent(minX, minY, maxX, maxY, mapSR)
      this.map.setExtent(extent, animate)
      console.log(`✅ 地图已自动缩放到 ${layerIds.length} 个图层的范围`)
    } catch (error) {
      console.error('缩放到多个图层范围失败:', error)
    }
  }

  /**
   * 移除图层
   * @param layerId 图层ID
   */
  removeLayer(layerId: string): void {
    const layer = this.map.getLayer(layerId)
    if (layer) {
      this.map.removeLayer(layer)
      console.log(`✅ 图层 ${layerId} 已移除`)
    }
  }

  /**
   * 清空图层
   * @param layerId 图层ID
   */
  clearLayer(layerId: string): void {
    const layer = this.map.getLayer(layerId)
    if (layer && layer.clear) {
      layer.clear()
      console.log(`✅ 图层 ${layerId} 已清空`)
    }
  }

  /**
   * 获取地图空间参考信息
   */
  getSpatialReferenceInfo(): any {
    if (!this.map) {
      return null
    }

    const mapSpatialRef = this.map.spatialReference
    const layers = this.map.layerIds || []

    return {
      map: {
        spatialReference: mapSpatialRef,
        wkid: mapSpatialRef ? mapSpatialRef.wkid : '未知'
      },
      layers: layers.map((layerId: string) => {
        const layer = this.map.getLayer(layerId)
        return {
          id: layerId,
          title: layer?.title || layer?.name || '无标题',
          wkid: layer?.spatialReference ? layer.spatialReference.wkid : '未知',
          visible: layer?.visible
        }
      })
    }
  }

  /**
   * 优化版批量绘制矩形 - 支持LOD和分批渲染
   * @param rectangles 矩形配置数组
   * @param layerId 图层ID
   * @param options 配置选项
   * @returns 图层实例
   */
  async drawMultipleRectanglesOptimized(
    rectangles: Array<Omit<RectangleConfig, 'layerId' | 'onClick'>>,
    layerId: string = 'multiRectangleLayer',
    options: {
      batchSize?: number // 每批绘制数量
      enableLOD?: boolean // 是否启用LOD优化
      maxDisplayCount?: number // 最大显示数量
      onClick?: (graphic: any) => void
      onProgress?: (current: number, total: number) => void
    } = {}
  ): Promise<any> {
    try {
      const {
        batchSize = 200,
        enableLOD = true,
        maxDisplayCount = 1000,
        onClick,
        onProgress
      } = options

      console.log(`🗺️ 开始优化批量绘制矩形，数量: ${rectangles.length}`)

      // LOD优化：根据数据量决定显示策略
      let displayRectangles = rectangles
      if (enableLOD && rectangles.length > maxDisplayCount) {
        console.log(`⚡ LOD优化：从 ${rectangles.length} 个矩形中筛选前 ${maxDisplayCount} 个高优先级矩形`)
        
        // 按人口密度排序，只显示前N个
        displayRectangles = [...rectangles]
          .sort((a, b) => {
            const popA = (a.attributes as any)?.totalPopulation || 0
            const popB = (b.attributes as any)?.totalPopulation || 0
            return popB - popA
          })
          .slice(0, maxDisplayCount)
      }

      // 获取或创建图层（不清空已存在的图层）
      const rectangleLayer = this.getOrCreateLayer(layerId, '批量矩形图层', true)

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()
      console.log('使用空间参考:', mapSR)

      let successCount = 0
      const totalBatches = Math.ceil(displayRectangles.length / batchSize)

      // 分批绘制
      for (let batchIndex = 0; batchIndex < totalBatches; batchIndex++) {
        const start = batchIndex * batchSize
        const end = Math.min((batchIndex + 1) * batchSize, displayRectangles.length)
        const batch = displayRectangles.slice(start, end)

        // 绘制这一批
        batch.forEach((rectConfig, index) => {
          try {
            const {
              bottomLeft,
              topRight,
              fillColor = [255, 0, 0, 0.5],
              outlineColor = [255, 255, 255, 0.8],
              outlineWidth = 1,
              attributes = {}
            } = rectConfig

            // 创建矩形几何体
            const extent = new this.esri.geometry.Extent(
              bottomLeft[0],
              bottomLeft[1],
              topRight[0],
              topRight[1],
              mapSR
            )

            // 创建矩形符号
            const symbol = new this.esri.symbol.SimpleFillSymbol(
              this.esri.symbol.SimpleFillSymbol.STYLE_SOLID,
              new this.esri.symbol.SimpleLineSymbol(
                this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
                new this.dojo.Color(outlineColor),
                outlineWidth
              ),
              new this.dojo.Color(fillColor)
            )

            // 创建图形
            const graphic = new this.esri.Graphic(extent, symbol, {
              ...attributes,
              batchIndex,
              index: start + index,
              bottomLeft,
              topRight
            })

            rectangleLayer.add(graphic)
            successCount++
          } catch (error) {
            console.error(`绘制第 ${start + index + 1} 个矩形失败:`, error)
          }
        })

        // 通知进度
        if (onProgress) {
          onProgress(successCount, displayRectangles.length)
        }

        // 给浏览器喘息时间
        if (batchIndex < totalBatches - 1) {
          await new Promise(resolve => setTimeout(resolve, 10))
        }
      }

      console.log(`✅ 优化批量矩形绘制完成，成功: ${successCount}/${displayRectangles.length}`)
      
      if (rectangles.length > displayRectangles.length) {
        console.log(`ℹ️ 已隐藏 ${rectangles.length - displayRectangles.length} 个低优先级矩形`)
      }

      // 添加点击事件
      if (onClick) {
        this.dojo.connect(rectangleLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      return rectangleLayer
    } catch (error: any) {
      console.error('优化批量绘制矩形失败:', error)
      throw error
    }
  }
  
  /**
   * 使用高性能方式绘制所有矩形（无LOD限制）
   * 使用Canvas渲染提升性能
   * @param rectangles 矩形配置数组
   * @param layerId 图层ID
   * @param options 配置选项
   */
  async drawAllRectanglesWithTileStrategy(
    rectangles: Array<Omit<RectangleConfig, 'layerId' | 'onClick'>>,
    layerId: string = 'tileRectangleLayer',
    options: {
      batchSize?: number
      simplifyRendering?: boolean // 简化渲染样式
      onClick?: (graphic: any) => void
      onProgress?: (current: number, total: number) => void
    } = {}
  ): Promise<any> {
    try {
      const {
        batchSize = 500, // 增大批次大小
        simplifyRendering = true, // 默认简化渲染
        onClick,
        onProgress
      } = options

      console.log(`🗺️ 使用瓦片策略绘制所有矩形，数量: ${rectangles.length}`)

      // 清除旧图层
      const existingLayer = this.map.getLayer(layerId)
      if (existingLayer) {
        this.map.removeLayer(existingLayer)
      }

      // 创建新的图形图层
      const rectangleLayer = new this.esri.layers.GraphicsLayer()
      rectangleLayer.id = layerId
      rectangleLayer.title = '职住表网格图层'
      
      this.map.addLayer(rectangleLayer)
      console.log('✅ 创建瓦片图层:', layerId)

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()
      console.log('使用空间参考:', mapSR)

      let successCount = 0
      const totalBatches = Math.ceil(rectangles.length / batchSize)
      
      // 预创建符号以减少对象创建开销
      const symbolCache = new Map<string, any>()

      // 分批绘制
      for (let batchIndex = 0; batchIndex < totalBatches; batchIndex++) {
        const start = batchIndex * batchSize
        const end = Math.min((batchIndex + 1) * batchSize, rectangles.length)
        const batch = rectangles.slice(start, end)

        // 批量创建图形
        const graphics: any[] = []
        
        batch.forEach((rectConfig, index) => {
          try {
            const {
              bottomLeft,
              topRight,
              fillColor = [255, 0, 0, 0.5],
              outlineColor = [255, 255, 255, 0.6],
              outlineWidth = 1,
              attributes = {}
            } = rectConfig

            // 创建矩形几何体
            const extent = new this.esri.geometry.Extent(
              bottomLeft[0],
              bottomLeft[1],
              topRight[0],
              topRight[1],
              mapSR
            )

            // 使用符号缓存减少对象创建
            const colorKey = `${fillColor.join(',')}`
            let symbol = symbolCache.get(colorKey)
            
            if (!symbol) {
              if (simplifyRendering) {
                // 简化渲染：更细的边框，减少渲染开销
                symbol = new this.esri.symbol.SimpleFillSymbol(
                  this.esri.symbol.SimpleFillSymbol.STYLE_SOLID,
                  new this.esri.symbol.SimpleLineSymbol(
                    this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
                    new this.dojo.Color(outlineColor),
                    0.5 // 极细边框
                  ),
                  new this.dojo.Color(fillColor)
                )
              } else {
                symbol = new this.esri.symbol.SimpleFillSymbol(
                  this.esri.symbol.SimpleFillSymbol.STYLE_SOLID,
                  new this.esri.symbol.SimpleLineSymbol(
                    this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
                    new this.dojo.Color(outlineColor),
                    outlineWidth
                  ),
                  new this.dojo.Color(fillColor)
                )
              }
              symbolCache.set(colorKey, symbol)
            }

            // 创建图形
            const graphic = new this.esri.Graphic(extent, symbol, {
              ...attributes,
              batchIndex,
              index: start + index,
              bottomLeft,
              topRight
            })

            graphics.push(graphic)
            successCount++
          } catch (error) {
            console.error(`创建第 ${start + index + 1} 个矩形失败:`, error)
          }
        })

        // 批量添加到图层（比逐个添加快很多）
        if (graphics.length > 0) {
          graphics.forEach(g => rectangleLayer.add(g))
        }

        // 通知进度
        if (onProgress) {
          onProgress(successCount, rectangles.length)
        }

        // 给浏览器喘息时间（缩短间隔）
        if (batchIndex < totalBatches - 1) {
          await new Promise(resolve => setTimeout(resolve, 5))
        }
      }

      console.log(`✅ 瓦片策略绘制完成，成功: ${successCount}/${rectangles.length}`)

      // 添加点击事件
      if (onClick) {
        this.dojo.connect(rectangleLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      // 启用图层的渲染优化
      if (rectangleLayer.setMaxAllowableOffset) {
        rectangleLayer.setMaxAllowableOffset(0.5) // 设置简化容差
      }

      return rectangleLayer
    } catch (error: any) {
      console.error('瓦片策略绘制失败:', error)
      throw error
    }
  }

  /**
   * GCJ-02（高德/国测局坐标）转 WGS84/CGCS2000 坐标
   * @param gcjLon GCJ-02经度
   * @param gcjLat GCJ-02纬度
   * @returns WGS84/CGCS2000 坐标 [经度, 纬度]
   */
  gcj02ToWgs84(gcjLon: number, gcjLat: number): [number, number] {
    // 判断是否在中国境外，如果在境外则不进行转换
    if (this.isOutOfChina(gcjLon, gcjLat)) {
      return [gcjLon, gcjLat]
    }

    // 使用迭代法进行精确转换
    let wgsLon = gcjLon
    let wgsLat = gcjLat
    
    for (let i = 0; i < 10; i++) {
      const [tempGcjLon, tempGcjLat] = this.wgs84ToGcj02(wgsLon, wgsLat)
      const dLon = tempGcjLon - gcjLon
      const dLat = tempGcjLat - gcjLat
      
      wgsLon -= dLon
      wgsLat -= dLat
      
      // 精度足够则提前退出
      if (Math.abs(dLon) < 1e-9 && Math.abs(dLat) < 1e-9) {
        break
      }
    }

    return [wgsLon, wgsLat]
  }

  /**
   * WGS84/CGCS2000 坐标转 GCJ-02（高德/国测局坐标）
   * @param wgsLon WGS84经度
   * @param wgsLat WGS84纬度
   * @returns GCJ-02坐标 [经度, 纬度]
   */
  wgs84ToGcj02(wgsLon: number, wgsLat: number): [number, number] {
    // 判断是否在中国境外，如果在境外则不进行转换
    if (this.isOutOfChina(wgsLon, wgsLat)) {
      return [wgsLon, wgsLat]
    }

    const { dLat, dLon } = this.delta(wgsLat, wgsLon)
    return [wgsLon + dLon, wgsLat + dLat]
  }

  /**
   * 计算坐标偏移量
   * @param lat 纬度
   * @param lon 经度
   * @returns 偏移量 { dLat, dLon }
   */
  private delta(lat: number, lon: number): { dLat: number; dLon: number } {
    const a = 6378245.0 // 长半轴
    const ee = 0.00669342162296594323 // 偏心率平方

    let dLat = this.transformLat(lon - 105.0, lat - 35.0)
    let dLon = this.transformLon(lon - 105.0, lat - 35.0)
    
    const radLat = (lat / 180.0) * Math.PI
    let magic = Math.sin(radLat)
    magic = 1 - ee * magic * magic
    const sqrtMagic = Math.sqrt(magic)
    
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * Math.cos(radLat) * Math.PI)
    
    return { dLat, dLon }
  }

  /**
   * 纬度转换
   */
  private transformLat(x: number, y: number): number {
    let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x))
    ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0
    ret += (20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin(y / 3.0 * Math.PI)) * 2.0 / 3.0
    ret += (160.0 * Math.sin(y / 12.0 * Math.PI) + 320 * Math.sin(y * Math.PI / 30.0)) * 2.0 / 3.0
    return ret
  }

  /**
   * 经度转换
   */
  private transformLon(x: number, y: number): number {
    let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x))
    ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0
    ret += (20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin(x / 3.0 * Math.PI)) * 2.0 / 3.0
    ret += (150.0 * Math.sin(x / 12.0 * Math.PI) + 300.0 * Math.sin(x / 30.0 * Math.PI)) * 2.0 / 3.0
    return ret
  }

  /**
   * 判断坐标是否在中国境外
   * @param lon 经度
   * @param lat 纬度
   * @returns 是否在中国境外
   */
  private isOutOfChina(lon: number, lat: number): boolean {
    // 中国大陆及周边范围
    if (lon < 72.004 || lon > 137.8347) {
      return true
    }
    if (lat < 0.8293 || lat > 55.8271) {
      return true
    }
    return false
  }

  /**
   * 批量转换高德坐标到当前地图坐标系
   * @param coordinates 高德坐标数组 [[lon, lat], [lon, lat], ...]
   * @returns 转换后的坐标数组
   */
  batchGcj02ToWgs84(coordinates: Array<[number, number]>): Array<[number, number]> {
    return coordinates.map(([lon, lat]) => this.gcj02ToWgs84(lon, lat))
  }

  /**
   * 解析坐标（支持数组和字符串两种格式）
   * @param coord 坐标数据，可以是 [lng, lat] 数组或 "lat,lng" 字符串
   * @returns 解析后的坐标 [经度, 纬度] 或 null
   */
  parseCoord(coord: any): [number, number] | null {
    if (!coord) return null
    
    // 如果是数组格式 [lng, lat]
    if (Array.isArray(coord) && coord.length === 2) {
      const lng = parseFloat(coord[0])
      const lat = parseFloat(coord[1])
      if (isNaN(lng) || isNaN(lat)) return null
      return [lng, lat]
    }
    
    // 如果是字符串格式 "lat,lng"
    if (typeof coord === 'string') {
      const parts = coord.split(',')
      if (parts.length !== 2) return null
      const lat = parseFloat(parts[0])
      const lng = parseFloat(parts[1])
      if (isNaN(lat) || isNaN(lng)) return null
      return [lng, lat] // ArcGIS 使用 [经度, 纬度]
    }
    
    return null
  }

  /**
   * 转换高德坐标字符串到当前地图坐标系
   * @param coordStr 高德坐标字符串 "lon,lat;lon,lat;..."
   * @returns 转换后的坐标字符串
   */
  convertGcj02StringToWgs84(coordStr: string): string {
    const coords = coordStr.split(';').map(pair => {
      const [lon, lat] = pair.split(',').map(Number)
      const [wgsLon, wgsLat] = this.gcj02ToWgs84(lon, lat)
      return `${wgsLon},${wgsLat}`
    })
    return coords.join(';')
  }

  /**
   * 绘制多边形（Polygon）
   * @param config 多边形配置
   * @returns 图层实例
   */
  drawPolygon(config: {
    coordinates: Array<[number, number]> | string  // 坐标数组或字符串 "lon,lat;lon,lat;..."
    fillColor?: [number, number, number, number]   // 填充颜色 RGBA
    outlineColor?: [number, number, number, number] // 边框颜色 RGBA
    outlineWidth?: number                           // 边框宽度
    layerId?: string                                // 图层ID
    attributes?: Record<string, any>                // 附加属性
    onClick?: (graphic: any) => void                // 点击回调
    convertFromGcj02?: boolean                      // 是否从高德坐标转换
  }): any {
    try {
      console.log('🔷 开始绘制多边形...')

      // 默认配置
      const {
        coordinates,
        fillColor = [0, 0, 255, 0.3],           // 蓝色半透明
        outlineColor = [0, 0, 255, 1],          // 蓝色边框
        outlineWidth = 2,
        layerId = 'polygonLayer',
        attributes = {},
        onClick,
        convertFromGcj02 = false
      } = config

      // 获取或创建图层
      const polygonLayer = this.getOrCreateLayer(layerId, '多边形图层')

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()

      // 处理坐标数据
      let coordArray: Array<[number, number]>
      
      if (typeof coordinates === 'string') {
        // 字符串格式：先转换为数组
        coordArray = coordinates.split(';').map(pair => {
          const [lon, lat] = pair.split(',').map(Number)
          return [lon, lat] as [number, number]
        })
      } else {
        coordArray = coordinates
      }

      // 如果需要从高德坐标转换
      if (convertFromGcj02) {
        console.log('🔄 正在从高德坐标转换...')
        coordArray = coordArray.map(([lon, lat]) => this.gcj02ToWgs84(lon, lat))
      }

      console.log(`📊 多边形顶点数: ${coordArray.length}`)

      // 创建多边形几何体
      const polygon = new this.esri.geometry.Polygon(mapSR)
      
      // 添加环（ring）- 外环
      const ring = coordArray.map(coord => [coord[0], coord[1]])
      polygon.addRing(ring)

      // 创建多边形符号
      const symbol = new this.esri.symbol.SimpleFillSymbol(
        this.esri.symbol.SimpleFillSymbol.STYLE_SOLID,
        new this.esri.symbol.SimpleLineSymbol(
          this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
          new this.dojo.Color(outlineColor),
          outlineWidth
        ),
        new this.dojo.Color(fillColor)
      )

      // 创建图形
      const graphic = new this.esri.Graphic(polygon, symbol, {
        ...attributes,
        type: 'polygon',
        vertexCount: coordArray.length
      })

      // 添加到图层
      polygonLayer.add(graphic)
      console.log('✅ 多边形绘制完成')

      // 添加点击事件
      if (onClick) {
        this.dojo.connect(polygonLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      return polygonLayer
    } catch (error: any) {
      console.error('绘制多边形失败:', error)
      throw error
    }
  }

  /**
   * 根据人口数量获取颜色
   * @param population 人口数量
   * @returns RGBA颜色数组
   */
  private getPopulationColor(population: number): [number, number, number, number] {
    if (population >= 5000) {
      return [255, 0, 0, 0.7] // 红色 - 高密度
    } else if (population >= 3000) {
      return [255, 165, 0, 0.6] // 橙色 - 中高密度
    } else if (population >= 1500) {
      return [255, 255, 0, 0.5] // 黄色 - 中等密度
    } else if (population >= 500) {
      return [0, 255, 0, 0.4] // 绿色 - 低密度
    } else {
      return [0, 0, 255, 0.3] // 蓝色 - 很低密度
    }
  }

  /**
   * 绘制职住表网格数据（整合版）
   * 接收职住表数据，自动处理并在地图上绘制网格
   * @param gridData 职住表数据数组
   * @param layerId 图层ID，默认为 'gridHomeworkLayer'
   * @param options 配置选项
   * @returns 图层实例
   */
  async drawGridHomeworkData(
    gridData: any[],
    layerId: string = 'gridHomeworkLayer',
    options: {
      batchSize?: number
      simplifyRendering?: boolean
      onClick?: (gridId: string, gridData: any) => void
      onProgress?: (current: number, total: number) => void
    } = {}
  ): Promise<any> {
    try {
      console.log('🗺️ 开始绘制职住表网格，数量:', gridData.length)

      const {
        batchSize = 500,
        simplifyRendering = true,
        onClick,
        onProgress
      } = options

      if (!gridData || gridData.length === 0) {
        console.warn('⚠️ 没有职住表数据可绘制')
        return null
      }

      // 准备矩形配置数组
      const rectangles = gridData.map((item: any) => {
        const bottomLeft = item.bottom_left_lng_lat
        const topRight = item.top_right_lng_lat
        const fillColor = this.getPopulationColor(item.total_population || 0)

        return {
          bottomLeft: [bottomLeft[0], bottomLeft[1]] as [number, number],
          topRight: [topRight[0], topRight[1]] as [number, number],
          fillColor: fillColor as [number, number, number, number],
          outlineColor: [255, 255, 255, 0.8] as [number, number, number, number],
          outlineWidth: 1,
          attributes: {
            gridId: item.grid_id,
            workPopulation: item.work_population,
            residePopulation: item.reside_population,
            totalPopulation: item.total_population,
            workRatio: item.work_ratio,
            resideRatio: item.reside_ratio,
            staMonth: item.sta_month,
            originalData: item
          }
        }
      })

      // 使用瓦片策略渲染所有数据
      const layer = await this.drawAllRectanglesWithTileStrategy(
        rectangles,
        layerId,
        {
          batchSize,
          simplifyRendering,
          onClick: onClick ? (graphic: any) => {
            if (graphic.attributes?.gridId) {
              onClick(graphic.attributes.gridId, graphic.attributes.originalData)
            }
          } : undefined,
          onProgress
        }
      )

      console.log('✅ 职住表网格绘制完成，共', rectangles.length, '个')

      return layer
    } catch (error: any) {
      console.error('❌ 绘制职住表网格失败:', error)
      throw error
    }
  }

  /**
   * 批量绘制线路（基于 POI 字符串）
   * 典型数据格式：
   * {
   *   pos: "lon,lat;lon,lat;...",
   *   line_name?: string,
   *   start_name?: string,
   *   ...其他字段
   * }
   * @param routes 线路数据数组
   * @param options 配置选项
   */
  drawMultiPolylines(
    routes: Array<{
      pos: string
      attributes?: Record<string, any>
      [key: string]: any
    }>,
    options: {
      layerId?: string
      colors?: Array<[number, number, number, number]>
      lineWidth?: number
      lineStyle?: 'solid' | 'dash' | 'dot' | 'dashdot' | 'dashdotdot'
      autoClear?: boolean
      autoZoom?: boolean
      convertFromGcj02?: boolean
      onClick?: (graphic: any, route: any) => void
      padding?: number
    } = {}
  ): any {
    console.log('🧵 开始批量绘制线路，数量:', routes?.length ?? 0)

    if (!routes || routes.length === 0) {
      console.warn('⚠️ 没有线路数据可绘制')
      return null
    }

    const {
      layerId = 'polylineLayer',
      colors = [
        [59, 130, 246, 0.8],  // 蓝色
        [16, 185, 129, 0.8],  // 绿色
        [245, 158, 11, 0.8],  // 橙色
        [239, 68, 68, 0.8],   // 红色
        [139, 92, 246, 0.8],  // 紫色
        [236, 72, 153, 0.8],  // 粉色
        [14, 165, 233, 0.8],  // 天蓝色
        [34, 197, 94, 0.8]    // 青绿色
      ],
      lineWidth = 3,
      lineStyle = 'solid' as 'solid' | 'dash' | 'dot' | 'dashdot' | 'dashdotdot',
      autoClear = true,
      autoZoom = true,
      convertFromGcj02 = true,
      onClick,
      padding = 0.01
    } = options

    // 清空图层并获取图层 / 空间参考
    const polylineLayer = this.getOrCreateLayer(layerId, '线路图层', autoClear)
    const mapSR = this.getMapSpatialReference()

    // 计算所有线路的边界范围，用于后续缩放
    let minLon = Infinity
    let maxLon = -Infinity
    let minLat = Infinity
    let maxLat = -Infinity
    let validRouteCount = 0

    routes.forEach((route, index) => {
      const pos = route.pos
      if (!pos || !pos.trim()) {
        console.warn(`⚠️ 线路 ${route.line_name || index} 没有 POI 数据`)
        return
      }

      const points = pos
        .split(';')
        .map(p => p.trim())
        .filter(p => !!p)

      if (points.length === 0) {
        console.warn(`⚠️ 线路 ${route.line_name || index} POI 数据为空`)
        return
      }

      // 每条线路对应一条折线路径
      const coordArray: Array<[number, number]> = []

      points.forEach(point => {
        const parts = point.split(',')
        if (parts.length !== 2) {
          console.warn(`⚠️ 坐标格式错误: ${point}`)
          return
        }

        const lon = Number(parts[0])
        const lat = Number(parts[1])

        if (isNaN(lon) || isNaN(lat)) {
          console.warn(`⚠️ 坐标包含 NaN: ${point}`)
          return
        }

        // 坐标转换：用于几何和边界计算
        const [wgsLon, wgsLat] = convertFromGcj02
          ? this.gcj02ToWgs84(lon, lat)
          : [lon, lat]

        coordArray.push([wgsLon, wgsLat])

        // 使用 WGS84 坐标参与边界计算
        if (wgsLon < minLon) minLon = wgsLon
        if (wgsLon > maxLon) maxLon = wgsLon
        if (wgsLat < minLat) minLat = wgsLat
        if (wgsLat > maxLat) maxLat = wgsLat
      })

      if (coordArray.length < 2) {
        console.warn(`⚠️ 线路 ${route.line_name || index} 有效坐标点不足，跳过`)
        return
      }

      const color =   [239, 68, 68, 0.8] //colors[index % colors.length]

      try {
        // 创建折线几何体（每条线路一条 Polyline）
        const polyline = new this.esri.geometry.Polyline(mapSR)
        const path = coordArray.map(coord => [coord[0], coord[1]])
        polyline.addPath(path)

        // 线型映射
        let lineStyleValue: any
        switch (lineStyle) {
          case 'dash':
            lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DASH
            break
          case 'dot':
            lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DOT
            break
          case 'dashdot':
            lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DASHDOT
            break
          case 'dashdotdot':
            lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DASHDOTDOT
            break
          default:
            lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_SOLID
        }

        // 创建符号
        const symbol = new this.esri.symbol.SimpleLineSymbol(
          lineStyleValue,
          new this.dojo.Color(color),
          lineWidth
        )

        // 图形属性：挂载原始 route 信息
        const graphicAttrs = {
          ...(route.attributes || {}),
          routeIndex: index,
          ...route
        }

        const graphic = new this.esri.Graphic(polyline, symbol, graphicAttrs)
        polylineLayer.add(graphic)

        validRouteCount += 1
      } catch (error) {
        console.error(`❌ 绘制线路 ${route.line_name || index} 失败:`, error)
      }
    })

    // 根据所有线路的整体范围进行缩放
    if (
      autoZoom &&
      validRouteCount > 0 &&
      minLon !== Infinity &&
      maxLon !== -Infinity &&
      minLat !== Infinity &&
      maxLat !== -Infinity
    ) {
      try {
        this.zoomToExtent([
          minLon - padding,
          minLat - padding,
          maxLon + padding,
          maxLat + padding
        ])
      } catch (error) {
        console.error('❌ 缩放到线路范围失败:', error)
      }
    }

    console.log(
      `✅ 批量线路绘制完成，有效线路数: ${validRouteCount} / ${routes.length}`
    )

    // 绑定点击事件（如果需要）
    if (onClick) {
      this.dojo.connect(polylineLayer, 'onClick', (event: any) => {
        const graphic = event.graphic
        if (!graphic) return
        const attrs = graphic.attributes || {}
        const routeIndex = typeof attrs.routeIndex === 'number' ? attrs.routeIndex : -1
        const route = routeIndex >= 0 && routeIndex < routes.length ? routes[routeIndex] : attrs
        onClick(graphic, route)
      })
    }

    return polylineLayer
  }

  /**
   * 绘制普通线条（Polyline）
   * @param config 线条配置
   * @returns 图层实例
   */
  drawPolyline(config: {
    coordinates: Array<[number, number]> | string  // 坐标数组或字符串 "lon,lat;lon,lat;..."
    lineColor?: [number, number, number, number]   // 线条颜色 RGBA
    lineWidth?: number                              // 线条宽度
    lineStyle?: 'solid' | 'dash' | 'dot' | 'dashdot' | 'dashdotdot'  // 线条样式
    layerId?: string                                // 图层ID
    attributes?: Record<string, any>                // 附加属性
    onClick?: (graphic: any) => void                // 点击回调
    convertFromGcj02?: boolean                      // 是否从高德坐标转换
  }): any {
    try {
      console.log('📏 开始绘制线条...')
      console.log('coordinates', config);
      // 默认配置
      const {
        coordinates,
        lineColor = [255, 0, 0, 1],             // 红色
        lineWidth = 3,
        lineStyle = 'solid',
        layerId = 'polylineLayer',
        attributes = {},
        onClick,
        convertFromGcj02 = false
      } = config

      // 获取或创建图层
      const polylineLayer = this.getOrCreateLayer(layerId, '线条图层')

      // 获取地图空间参考
      const mapSR = this.getMapSpatialReference()

      // 处理坐标数据
      let coordArray: Array<[number, number]>
      
      if (typeof coordinates === 'string') {
        // 字符串格式：先转换为数组
        coordArray = coordinates.split(';').map(pair => {
          const [lon, lat] = pair.split(',').map(Number)
          return [lon, lat] as [number, number]
        })
      } else {
        coordArray = coordinates
      }

      // 如果需要从高德坐标转换
      if (convertFromGcj02) {
        console.log('🔄 正在从高德坐标转换...')
        coordArray = coordArray.map(([lon, lat]) => this.gcj02ToWgs84(lon, lat))
      }

      console.log(`📊 线条节点数: ${coordArray.length}`)

      // 创建折线几何体
      const polyline = new this.esri.geometry.Polyline(mapSR)
      
      // 添加路径
      const path = coordArray.map(coord => [coord[0], coord[1]])
      polyline.addPath(path)

      // 确定线条样式
      let lineStyleValue: any
      switch (lineStyle) {
        case 'dash':
          lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DASH
          break
        case 'dot':
          lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DOT
          break
        case 'dashdot':
          lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DASHDOT
          break
        case 'dashdotdot':
          lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_DASHDOTDOT
          break
        default:
          lineStyleValue = this.esri.symbol.SimpleLineSymbol.STYLE_SOLID
      }

      // 创建线条符号
      const symbol = new this.esri.symbol.SimpleLineSymbol(
        lineStyleValue,
        new this.dojo.Color(lineColor),
        lineWidth
      )

      // 创建图形
      const graphic = new this.esri.Graphic(polyline, symbol, {
        ...attributes,
        type: 'polyline',
        nodeCount: coordArray.length
      })

      // 添加到图层
      polylineLayer.add(graphic)
      console.log('✅ 线条绘制完成')

      // 添加点击事件
      if (onClick) {
        this.dojo.connect(polylineLayer, 'onClick', (event: any) => {
          const graphic = event.graphic
          if (graphic) {
            onClick(graphic)
          }
        })
      }

      return polylineLayer
    } catch (error: any) {
      console.error('绘制线条失败:', error)
      throw error
    }
  }

  /**
   * 批量绘制多个点（站点）
   * @param points 点数据数组
   * @param options 配置选项
   * @returns 图层实例
   */
  drawMultiPoints(
    points: Array<{
      lon84: number
      lat84: number
      id?: string
      stop_name?: string
      [key: string]: any
    }>,
    options: {
      layerId?: string
      markerColor?: [number, number, number, number]  // 标记颜色 RGBA
      markerSize?: number                              // 标记大小
      markerStyle?: 'circle' | 'square' | 'cross' | 'x' | 'diamond'  // 标记样式
      autoClear?: boolean                              // 是否自动清空图层
      autoZoom?: boolean                               // 是否自动缩放
      onClick?: (graphic: any, point: any) => void   // 点击回调
      padding?: number                                 // 缩放边距
    } = {}
  ): any {
    console.log('📍 开始批量绘制站点，数量:', points?.length ?? 0)

    if (!points || points.length === 0) {
      console.warn('⚠️ 没有站点数据可绘制')
      return null
    }

    const {
      layerId = 'stopsLayer',
      markerColor = [59, 130, 246, 0.8],  // 蓝色
      markerSize = 12,
      markerStyle = 'circle',
      autoClear = true,
      autoZoom = true,
      onClick,
      padding = 0.01
    } = options

    // 清空图层并获取图层 / 空间参考
    const pointsLayer = this.getOrCreateLayer(layerId, '站点图层', autoClear)
    const mapSR = this.getMapSpatialReference()

    // 计算所有站点的边界范围，用于后续缩放
    let minLon = Infinity
    let maxLon = -Infinity
    let minLat = Infinity
    let maxLat = -Infinity
    let validPointCount = 0

    // 确定标记样式
    let markerStyleValue: any
    switch (markerStyle) {
      case 'square':
        markerStyleValue = this.esri.symbol.SimpleMarkerSymbol.STYLE_SQUARE
        break
      case 'cross':
        markerStyleValue = this.esri.symbol.SimpleMarkerSymbol.STYLE_CROSS
        break
      case 'x':
        markerStyleValue = this.esri.symbol.SimpleMarkerSymbol.STYLE_X
        break
      case 'diamond':
        markerStyleValue = this.esri.symbol.SimpleMarkerSymbol.STYLE_DIAMOND
        break
      default:
        markerStyleValue = this.esri.symbol.SimpleMarkerSymbol.STYLE_CIRCLE
    }

    // 创建标记符号
    const symbol = new this.esri.symbol.SimpleMarkerSymbol(
      markerStyleValue,
      markerSize,
      new this.esri.symbol.SimpleLineSymbol(
        this.esri.symbol.SimpleLineSymbol.STYLE_SOLID,
        new this.dojo.Color([255, 255, 255]),
        2
      ),
      new this.dojo.Color(markerColor)
    )

    points.forEach((point, index) => {
      const { lon84, lat84 } = point

      if (lon84 === undefined || lat84 === undefined || isNaN(lon84) || isNaN(lat84)) {
        console.warn(`⚠️ 站点 ${point.stop_name || index} 坐标无效`)
        return
      }

      try {
        // 创建点几何体
        const pointGeometry = new this.esri.geometry.Point(lon84, lat84, mapSR)

        // 图形属性：挂载原始 point 信息
        const graphicAttrs = {
          pointIndex: index,
          ...point
        }

        const graphic = new this.esri.Graphic(pointGeometry, symbol, graphicAttrs)
        pointsLayer.add(graphic)

        // 更新边界范围
        if (lon84 < minLon) minLon = lon84
        if (lon84 > maxLon) maxLon = lon84
        if (lat84 < minLat) minLat = lat84
        if (lat84 > maxLat) maxLat = lat84

        validPointCount += 1
      } catch (error) {
        console.error(`❌ 绘制站点 ${point.stop_name || index} 失败:`, error)
      }
    })

    // 根据所有站点的整体范围进行缩放
    if (
      autoZoom &&
      validPointCount > 0 &&
      minLon !== Infinity &&
      maxLon !== -Infinity &&
      minLat !== Infinity &&
      maxLat !== -Infinity
    ) {
      try {
        this.zoomToExtent([
          minLon - padding,
          minLat - padding,
          maxLon + padding,
          maxLat + padding
        ])
      } catch (error) {
        console.error('❌ 缩放到站点范围失败:', error)
      }
    }

    console.log(
      `✅ 批量站点绘制完成，有效站点数: ${validPointCount} / ${points.length}`
    )

    // 绑定点击事件（如果需要）
    if (onClick) {
      this.dojo.connect(pointsLayer, 'onClick', (event: any) => {
        const graphic = event.graphic
        if (!graphic) return
        const attrs = graphic.attributes || {}
        const pointIndex = typeof attrs.pointIndex === 'number' ? attrs.pointIndex : -1
        const point = pointIndex >= 0 && pointIndex < points.length ? points[pointIndex] : attrs
        onClick(graphic, point)
      })
    }

    return pointsLayer
  }
}

/**
 * 创建地图工具实例
 * @param map 地图实例
 * @param esri ArcGIS API
 * @param dojo Dojo API
 * @returns 地图工具实例
 */
export function createMapUtils(map: any, esri: any, dojo: any): ArcGISMapUtils {
  return new ArcGISMapUtils(map, esri, dojo)
}

