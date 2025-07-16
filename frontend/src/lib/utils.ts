import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import getConfig from 'next/config'

/**
 * 合并Tailwind CSS类
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * 获取运行时配置
 */
export function getRuntimeConfig() {
  const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} }
  return publicRuntimeConfig
}

/**
 * 给URL添加basePath前缀
 * @param path - 需要添加前缀的路径
 * @returns 添加了前缀的完整路径
 */
export function getUrl(path: string): string {
  const { basePath = '' } = getRuntimeConfig()
  
  // 如果路径已经是完整URL，则直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  
  // 确保path以/开头
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  
  // 组合basePath和path，避免重复的斜杠
  return `${basePath}${normalizedPath}`
}

/**
 * 获取API URL前缀
 * @param endpoint - API端点路径
 * @returns 添加了API前缀的完整API URL
 */
export function getApiUrl(endpoint: string): string {
  return 'http://localhost:8000' + endpoint
}
