/*
 * @Description: 
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-09 15:13:09
 * @LastEditors: 王晨
 * @LastEditTime: 2025-11-05 17:37:35
 */
import { toRaw } from 'vue';
import { DictionaryStore } from '/@/stores/dictionary';

/**
  * @method 获取指定name字典
  */
export const dictionary = (name: string,key?:string|number|undefined) => {
  const dict = DictionaryStore() 
  const dictionary = toRaw(dict.data)
  console.log('line_type字典:', dict.data.line_type)
  if(key!=undefined){
    const obj = dictionary[name].find((item:any) => item.value == key)
    return obj?obj.label:''
  }else{
    return dictionary[name]
  }
}
