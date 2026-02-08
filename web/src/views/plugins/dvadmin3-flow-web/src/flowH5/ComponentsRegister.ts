import { App, defineAsyncComponent } from 'vue';
import Vant from "vant";
import 'vant/lib/index.css';
import VantKit from '@meetjs/vant4-kit'
import '@meetjs/vant4-kit/dist/index.css'
import Previewer from "./Previewer.vue"

// 定义异步组件的类型
interface AsyncComponent {
    name: string;
    componentPath: any; // 使用 defineAsyncComponent 返回值
}

// 同步组件列表
const components = [Previewer];

// 异步组件列表
let asyncComponents: AsyncComponent[] = [];

// 动态注册组件函数
function registerComponents() {
    const files = import.meta.glob('./components/**/index.vue');
    for (const file of Object.keys(files)) {
        try {
            // 匹配文件名和路径
            const m =
                file.match(/^\.\/(?<name>\w+)\.(tsx|vue)$/i) ||
                file.match(/^\.\/((?<name>\w+)\/)+index\.(tsx|vue)$/i);

            if (m?.groups?.name) {
                const componentName = m.groups.name;
                const componentPath = defineAsyncComponent(files[file]);

                // 检查是否已注册过该组件
                if (!asyncComponents.some(c => c.name === componentName)) {
                    asyncComponents.push({ name: componentName, componentPath });
                }
            } else {
                console.warn(`无法解析文件名: ${file}`);
            }
        } catch (error) {
            console.error(`注册组件时出错: ${file}`, error);
        }
    }
}

// 缓存注册结果，避免重复扫描
if (asyncComponents.length === 0) {
    registerComponents();
}

// 插件定义
export default {
    install(app: App) {
        // 注册同步组件
        components.forEach((item) => {
            if (!app.component(item.name)) {
                app.component(item.name, item);
            }
        });

        // 注册异步组件
        asyncComponents.forEach((item) => {
            if (!app.component(item.name)) {
                console.log("异步注册组件:", item.name)
                app.component(item.name, item.componentPath);
            }
        });

        // 注册 Vant 组件库
        app.use(Vant);
        // Lazyload 指令需要单独进行注册
        app.use(Vant.Lazyload);
        app.use(VantKit);
    },
};
