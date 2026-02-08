/**
 * Learun 工具类
 * 参考力软原始代码，提供常用的工具方法
 */

import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import type { LoadingInstance } from 'element-plus/es/components/loading/src/loading'
import request from '/@/utils/request'

class Learun {
  private loadingInstance: LoadingInstance | null = null

  /**
   * 生成UUID (GUID)
   * @returns {string} UUID字符串
   */
  newGuid(): string {
    // 使用浏览器原生API生成UUID v4
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID()
    }
    
    // 降级方案：手写UUID生成器
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0
      const v = c === 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
  }

  /**
   * 生成短GUID (不带连字符)
   * @returns {string} 短GUID字符串
   */
  shortGuid(): string {
    return this.newGuid().replace(/-/g, '')
  }

  /**
   * 确认对话框
   * @param {string} message - 提示消息
   * @param {Function} callback - 回调函数 (res, index) => void
   */
  layerConfirm(message: string, callback: (res: boolean, index?: any) => void): void {
    ElMessageBox.confirm(message, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    })
      .then(() => {
        callback(true)
      })
      .catch((action) => {
        if (action === 'cancel') {
          callback(false)
        }
      })
  }

  /**
   * 弹层表单
   * @param {Object} options - 配置选项
   * @param {string} options.id - 弹层ID
   * @param {string} options.title - 标题
   * @param {string} options.url - URL地址
   * @param {number} options.width - 宽度
   * @param {number} options.height - 高度
   * @param {Function} options.callBack - 回调函数
   * @param {boolean} options.maxmin - 是否显示最大化最小化按钮
   * @param {any} options.btn - 按钮配置
   */
  layerForm(options: {
    id: string
    title: string
    url: string
    width?: number
    height?: number
    callBack?: (id: string) => any
    maxmin?: boolean
    btn?: any
  }): void {
    console.log('layerForm 暂未实现，配置:', options)
    // TODO: 实现弹层表单逻辑
    // 可以使用 ElDialog 或第三方弹层库
  }

  /**
   * 加载提示
   * @param {boolean} show - 是否显示
   * @param {string} text - 提示文本
   */
  loading(show: boolean, text?: string): void {
    if (show) {
      this.loadingInstance = ElLoading.service({
        lock: true,
        text: text || '加载中...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
    } else {
      this.loadingInstance?.close()
      this.loadingInstance = null
    }
  }

  /**
   * 提示消息
   */
  alert = {
    success: (message: string) => {
      ElMessage.success(message)
    },
    error: (message: string) => {
      ElMessage.error(message)
    },
    warning: (message: string) => {
      ElMessage.warning(message)
    },
    info: (message: string) => {
      ElMessage.info(message)
    }
  }

  /**
   * HTTP异步POST请求
   * @param {string} url - 请求地址
   * @param {any} data - 请求数据
   * @param {Function} callback - 回调函数
   */
  httpAsyncPost(url: string, data: any, callback: (res: any) => void): void {
    request({
      url,
      method: 'post',
      data
    }).then((res: any) => {
      callback(res)
    }).catch((err: any) => {
      console.error('httpAsyncPost error:', err)
      // 也可以选择调用 callback(err) 或者不调用，视业务需求而定
      // 力软原有逻辑可能是失败也回调，这里暂不做处理，依赖 request 的拦截器提示
    })
  }

  /**
   * 语言翻译（简化版，直接返回原文）
   */
  language = {
    getSyn: (text: string) => {
      return text
    }
  }

  /**
   * 客户端数据缓存（简化版）
   */
  clientdata = {
    get: (keys: string[]) => {
      // TODO: 实现客户端数据获取
      return {}
    },
    getAsync: (type: string, options: any) => {
      // TODO: 实现异步数据获取
      console.log('clientdata.getAsync 暂未实现:', type, options)
    }
  }

  /**
   * frame标签页操作（简化版）
   */
  frameTab = {
    close: (id: string) => {
      console.log('frameTab.close 暂未实现:', id)
    },
    parentIframe: () => {
      return {
        refreshGirdData: () => {
          console.log('refreshGirdData 暂未实现')
        }
      }
    }
  }
}

// 创建单例
const learun = new Learun()

// 挂载到window（兼容老代码）
declare global {
  interface Window {
    learun: any
  }
}

if (typeof window !== 'undefined') {
  window.learun = learun
}

export default learun
export { learun }
