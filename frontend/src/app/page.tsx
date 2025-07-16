"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Link, Upload, Mic, Globe, Sparkles, Loader2, X, AlertCircle, Plus, Play, Pause, StopCircle, Edit, Save } from "lucide-react"
import { getApiUrl, getUrl } from "@/lib/utils"

// 音色数据
const voiceOptions = [
  { id: "alex", name: "Alex", type: "男声", description: "温和专业，适合商务内容", sampleUrl: "/samples/alex.mp3" },
  { id: "sarah", name: "Sarah", type: "女声", description: "清晰亲和，适合教育内容", sampleUrl: "/samples/sarah.mp3" },
  { id: "david", name: "David", type: "男声", description: "深沉磁性，适合故事叙述", sampleUrl: "/samples/david.mp3" },
  { id: "emily", name: "Emily", type: "女声", description: "活泼自然，适合生活分享", sampleUrl: "/samples/emily.mp3" },
  { id: "james", name: "James", type: "男声", description: "权威稳重，适合新闻播报", sampleUrl: "/samples/james.mp3" },
  { id: "lisa", name: "Lisa", type: "女声", description: "优雅知性，适合文化艺术", sampleUrl: "/samples/lisa.mp3" },
  { id: "michael", name: "Michael", type: "男声", description: "年轻活力，适合科技话题", sampleUrl: "/samples/michael.mp3" },
  // { id: "anna", name: "Anna", type: "女声", description: "甜美温柔，适合情感内容", sampleUrl: "/samples/anna.mp3" },
  // { id: "robert", name: "Robert", type: "男声", description: "成熟稳健，适合财经分析", sampleUrl: "/samples/robert.mp3" },
  { id: "sophia", name: "Sophia", type: "女声", description: "国际范，适合多元文化", sampleUrl: "/samples/sophia.mp3" }
]

// 内容类型数据
const defaultContentTypes = [
  { id: "news", name: "新闻评论" },
  { id: "event", name: "事件追踪" },
  { id: "product", name: "产品介绍" },
  { id: "story", name: "儿童故事" },
  { id: "knowledge", name: "知识分享" }
]


export default function Home() {
  const [content, setContent] = useState("")
  const [language, setLanguage] = useState("chinese")
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedVoices, setSelectedVoices] = useState<string[]>(["alex"])
  const [isVoiceDialogOpen, setIsVoiceDialogOpen] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [generateSuccess, setGenerateSuccess] = useState<string | null>(null)
  const [generatedText, setGeneratedText] = useState("")
  const [contentType, setContentType] = useState("knowledge")
  const [contentTypes, setContentTypes] = useState(defaultContentTypes)
  const [isContentTypeDialogOpen, setIsContentTypeDialogOpen] = useState(false)
  const [customContentType, setCustomContentType] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [editableText, setEditableText] = useState("")
  const [podcastList, setPodcastList] = useState<any[]>([])
  const [isLoadingList, setIsLoadingList] = useState(false)
  const [listError, setListError] = useState<string | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedPodcast, setSelectedPodcast] = useState<any>(null)


  // 获取播客列表
  const fetchPodcastList = async () => {
    setIsLoadingList(true)
    setListError(null)
    try {
      const res = await fetch(getApiUrl('/podcast/list'))
      if (!res.ok) throw new Error('获取播客列表失败')
      const data = await res.json()
      setPodcastList(Array.isArray(data.items) ? data.items : [])
    } catch (e: any) {
      setListError(e.message || '获取失败')
    } finally {
      setIsLoadingList(false)
    }
  }

  // 页面加载时获取列表
  useEffect(() => {
    fetchPodcastList()
  }, [])
  


  const handleGenerate = async () => {
    if (!content.trim()) return
  
    setIsGenerating(true)
    setGenerateError(null)
    setGenerateSuccess(null)
    setGeneratedText("")
  
    try {
      const requestData = {
        content: content.trim(),
        language,
        voices: selectedVoices,
        contentType,
        timestamp: new Date().toISOString()
      }
  
      const response = await fetch(getApiUrl('/podcast/generate_script'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })
  
      if (!response.ok || !response.body) {
        const errorText = await response.text().catch(() => '')
        throw new Error(`服务器错误: ${response.status}\n${errorText}`)
      }
  
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
  
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
  
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
  
        buffer = lines.pop() || ''
  
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const jsonStr = line.replace(/^data:\s*/, '')
            try {
              const parsed = JSON.parse(jsonStr)
              if (parsed.text) {
                setGeneratedText(prev => prev + parsed.text)
              }
            } catch (e) {
              console.warn('解析失败:', jsonStr)
            }
          }
        }
      }
  
      setGenerateSuccess("播客生成成功！")
      fetchPodcastList(); // 创建成功后自动刷新列表
    } catch (error) {
      console.error('生成失败:', error)
      const errorMessage = error instanceof Error ? error.message : '生成失败，请稍后重试'
      setGenerateError(errorMessage)
    } finally {
      setIsGenerating(false)
    }
  }
  


  const handleVoiceToggle = (voiceId: string) => {
    setSelectedVoices(prev => {
      if (prev.includes(voiceId)) {
        return prev.filter(id => id !== voiceId)
      } else if (prev.length < 5) {
        return [...prev, voiceId]
      }
      return prev
    })
  }

  const removeVoice = (voiceId: string) => {
    setSelectedVoices(prev => prev.filter(id => id !== voiceId))
  }

  const getSelectedVoicesText = () => {
    if (selectedVoices.length === 0) return "未选择音色"
    if (selectedVoices.length === 1) return "已选 1 种音色"
    return `已选 ${selectedVoices.length} 种音色`
  }

  const addCustomContentType = () => {
    if (!customContentType.trim()) return
    
    const newType = {
      id: `custom_${Date.now()}`,
      name: customContentType.trim()
    }
    
    setContentTypes(prev => [...prev, newType])
    setCustomContentType("")
    setContentType(newType.id)
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    try {
      if (file.type === 'text/plain') {
        const text = await file.text()
        setContent(text)
        console.log('文本文件内容已加载')
      } else if (file.type === 'application/pdf') {
        // PDF处理需要额外库，这里只是简单提示
        setContent(`正在处理PDF文件: ${file.name}\n\n请在此处编辑提取的内容...`)
        console.log('PDF文件已选择，但需要额外处理')
      } else {
        alert('仅支持TXT和PDF文件')
      }
    } catch (error) {
      console.error('文件处理错误:', error)
      alert('文件处理失败')
    }
    
    // 重置文件输入框
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const playVoiceSample = (voiceId: string) => {
    // 如果当前有音频在播放，先停止
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    // 如果点击的是当前播放的音色，则停止播放
    if (currentlyPlaying === voiceId) {
      setCurrentlyPlaying(null)
      return
    }

    // 获取当前选择的音色
    const voice = voiceOptions.find(v => v.id === voiceId)
    if (!voice) return

    try {
      // 创建新的音频实例，使用getUrl确保路径正确
      const audio = new Audio(getUrl(voice.sampleUrl))
      
      // 设置播放完成后的回调
      audio.onended = () => {
        setCurrentlyPlaying(null)
      }
      
      // 设置错误处理
      audio.onerror = () => {
        console.error("音频示例加载失败")
        setCurrentlyPlaying(null)
        // 实际应用中可以显示错误提示
        // alert(`无法播放音色示例，请确保音频文件 ${voice.sampleUrl} 存在`)
        alert("音频示例加载失败")
      }
      
      // 开始播放
      audio.play()
        .then(() => {
          // 播放成功，更新状态
          audioRef.current = audio
          setCurrentlyPlaying(voiceId)
        })
        .catch(error => {
          console.error("播放失败:", error)
          setCurrentlyPlaying(null)
        })
    } catch (error) {
      console.error("音频初始化错误:", error)
    }
  }

  // 组件卸载时停止播放
  const stopAllAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
      setCurrentlyPlaying(null)
    }
  }

  // 开始编辑生成的内容
  const startEditing = () => {
    setIsEditing(true)
    setEditableText(generatedText)
  }

  // 取消编辑
  const cancelEditing = () => {
    setIsEditing(false)
  }

  // 更新生成的内容
  const updateGeneratedContent = async () => {
    if (!editableText.trim()) return

    setIsUpdating(true)
    try {
      const requestData = {
        content: editableText.trim(),
        language,
        voices: selectedVoices,
        contentType,
        timestamp: new Date().toISOString()
      }

      const response = await fetch(getApiUrl('/podcast/update_script'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => '')
        throw new Error(`更新失败: ${response.status}\n${errorText}`)
      }

      const result = await response.json()
      
      // 更新成功后保存更新的内容
      setGeneratedText(editableText)
      setIsEditing(false)
      setGenerateSuccess("播客内容已更新！")
    } catch (error) {
      console.error('更新失败:', error)
      const errorMessage = error instanceof Error ? error.message : '更新失败，请稍后重试'
      setGenerateError(errorMessage)
    } finally {
      setIsUpdating(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex flex-col items-center justify-center p-4 md:p-6">
      <div className="w-full max-w-4xl mx-auto space-y-8">
        {/* Logo and Title */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            {/* Soundwave Icon */}
            <div className="flex items-center gap-1">
              <div className="w-1.5 h-8 bg-gradient-to-t from-blue-500 to-cyan-400 rounded-full animate-pulse"></div>
              <div className="w-1.5 h-12 bg-gradient-to-t from-cyan-400 to-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
              <div className="w-1.5 h-6 bg-gradient-to-t from-blue-600 to-sky-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
              <div className="w-1.5 h-10 bg-gradient-to-t from-sky-400 to-blue-500 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
              <div className="w-1.5 h-7 bg-gradient-to-t from-blue-500 to-cyan-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
            </div>

            {/* ListenHub Text */}
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 via-cyan-500 via-sky-500 to-blue-600 bg-clip-text text-transparent">
              ListenHub
            </h1>
          </div>

          <p className="text-xl md:text-2xl text-slate-700 font-medium">每一次记录，都值得分享
          </p>
        </div>

        {/* Main Input Area */}
        <div className="w-full max-w-3xl mx-auto">
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="写下你想听 AI 聊聊的内容"
            className="min-h-[200px] text-lg border-slate-200 rounded-2xl resize-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 bg-white/90 backdrop-blur-sm shadow-lg transition-all duration-200 hover:shadow-xl hover:shadow-blue-100/50"
          />
        </div>

        {/* Selected Voices Display */}
        {selectedVoices.length > 0 && (
          <div className="w-full max-w-3xl mx-auto">
            <div className="flex flex-wrap gap-2">
              {selectedVoices.map(voiceId => {
                const voice = voiceOptions.find(v => v.id === voiceId)
                return (
                  <div key={voiceId} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                    <span>{voice?.name} ({voice?.type})</span>
                    <button onClick={() => removeVoice(voiceId)} className="hover:bg-blue-200 rounded-full p-0.5">
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Bottom Controls */}
        <div className="w-full max-w-3xl mx-auto bg-white/90 backdrop-blur-sm rounded-2xl p-4 md:p-6 border border-slate-200 shadow-lg shadow-blue-100/30">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Left Controls */}
            <div className="flex items-center gap-2 md:gap-4 flex-wrap">
              <Dialog open={isContentTypeDialogOpen} onOpenChange={setIsContentTypeDialogOpen}>
                <Select value={contentType} onValueChange={setContentType}>
                  <SelectTrigger className="w-32 md:w-36 border-0 bg-transparent hover:bg-blue-50 transition-colors">
                    <Sparkles className="w-4 h-4 mr-1 md:mr-2" />
                    <SelectValue placeholder="内容类型" />
                  </SelectTrigger>
                  <SelectContent>
                    {contentTypes.map((type) => (
                      <SelectItem key={type.id} value={type.id}>{type.name}</SelectItem>
                    ))}
                    <DialogTrigger asChild>
                      <div className="flex items-center px-2 py-1.5 text-sm text-blue-600 hover:bg-blue-50 cursor-pointer rounded-sm">
                        <Plus className="w-4 h-4 mr-2" />
                        自定义类型
                      </div>
                    </DialogTrigger>
                  </SelectContent>
                </Select>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>添加自定义内容类型</DialogTitle>
                    <DialogDescription>
                      创建一个新的内容类型，以满足您的特定需求
                    </DialogDescription>
                  </DialogHeader>
                  
                  <div className="mt-4 space-y-4">
                    <div className="space-y-2">
                      <label htmlFor="custom-type" className="text-sm font-medium">
                        类型名称
                      </label>
                      <div className="flex gap-2">
                        <Textarea 
                          id="custom-type"
                          value={customContentType}
                          onChange={(e) => setCustomContentType(e.target.value)}
                          placeholder="输入自定义内容类型名称"
                          className="resize-none"
                        />
                      </div>
                    </div>
                    
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setIsContentTypeDialogOpen(false)}>
                        取消
                      </Button>
                      <Button 
                        onClick={() => {
                          addCustomContentType()
                          setIsContentTypeDialogOpen(false)
                        }}
                        disabled={!customContentType.trim()}
                      >
                        添加
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
              
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger className="w-28 md:w-32 border-0 bg-transparent hover:bg-blue-50 transition-colors">
                  <Globe className="w-4 h-4 mr-1 md:mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="chinese">中文</SelectItem>
                  <SelectItem value="spanish">Español</SelectItem>
                  <SelectItem value="french">Français</SelectItem>
                  <SelectItem value="japanese">日本語</SelectItem>
                </SelectContent>
              </Select>

              <Dialog open={isVoiceDialogOpen} onOpenChange={setIsVoiceDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="text-slate-600 hover:text-slate-800 hover:bg-blue-50 transition-colors">
                    <Mic className="w-4 h-4 mr-2" />
                    <span className="hidden sm:inline">{getSelectedVoicesText()}</span>
                    <span className="sm:hidden">音色</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>选择播客音色</DialogTitle>
                    <DialogDescription>
                      最多可选择 5 种不同的音色来丰富你的播客内容 ({selectedVoices.length}/5)
                    </DialogDescription>
                  </DialogHeader>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    {voiceOptions.map((voice) => (
                      <div key={voice.id} className="border rounded-lg p-4 hover:bg-slate-50 transition-colors">
                        <div className="flex items-start space-x-3">
                          <Checkbox
                            id={voice.id}
                            checked={selectedVoices.includes(voice.id)}
                            onCheckedChange={() => handleVoiceToggle(voice.id)}
                            disabled={!selectedVoices.includes(voice.id) && selectedVoices.length >= 5}
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <label htmlFor={voice.id} className="cursor-pointer">
                                <div className="font-medium text-slate-900">{voice.name}</div>
                              </label>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0 rounded-full"
                                onClick={() => playVoiceSample(voice.id)}
                              >
                                {currentlyPlaying === voice.id ? (
                                  <Pause className="h-4 w-4" />
                                ) : (
                                  <Play className="h-4 w-4" />
                                )}
                                <span className="sr-only">播放{voice.name}示例</span>
                              </Button>
                            </div>
                            <div className="text-sm text-blue-600 font-medium">{voice.type}</div>
                            <div className="text-sm text-slate-500 mt-1">{voice.description}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-between items-center mt-6 pt-4 border-t">
                    <span className="text-sm text-slate-500">
                      {selectedVoices.length === 5 ? "已达到最大选择数量" : `还可选择 ${5 - selectedVoices.length} 种音色`}
                    </span>
                    <Button onClick={() => {
                      setIsVoiceDialogOpen(false)
                      stopAllAudio()
                    }} className="bg-blue-600 hover:bg-blue-700">
                      确认选择
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* Right Controls */}
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="icon" className="text-slate-600 hover:text-slate-800 hover:bg-blue-50 transition-colors">
                <Link className="w-4 h-4" />
              </Button>

              {/* 隐藏的文件输入 */}
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".txt,.pdf,text/plain,application/pdf"
                onChange={handleFileUpload}
              />

              <Button 
                variant="ghost" 
                size="icon" 
                className="text-slate-600 hover:text-slate-800 hover:bg-blue-50 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-4 h-4" />
              </Button>

              <Button
                onClick={handleGenerate}
                disabled={!content.trim() || isGenerating}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-slate-400 disabled:to-slate-400 text-white px-6 md:px-8 py-2 rounded-full font-medium transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl disabled:hover:scale-100"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    生成中...
                  </>
                ) : (
                  "创建"
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Features Hint */}
        <div className="text-center text-slate-500 text-sm max-w-2xl mx-auto">
          <p>支持多语言生成，可选择不同的 AI 声音，上传文档或链接作为内容源</p>
        </div>

        {/* Error Message */}
        {generateError && (
          <div className="w-full max-w-3xl mx-auto bg-red-50 border border-red-200 rounded-2xl p-4">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">生成失败</span>
            </div>
            <p className="text-red-700 mt-1">{generateError}</p>
          </div>
        )}

        {/* Success Message with Editable Content */}
        {generateSuccess && (
          <div className="w-full max-w-3xl mx-auto bg-green-50 border border-green-200 rounded-2xl p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-green-800">
                <Sparkles className="w-5 h-5" />
                <span className="font-medium">生成成功</span>
              </div>
              
              {generatedText && (
                <div className="flex items-center gap-2">
                  {isEditing ? (
                    <>
                      <Button 
                        onClick={updateGeneratedContent} 
                        disabled={isUpdating} 
                        variant="outline" 
                        size="sm" 
                        className="flex items-center gap-1 text-green-700 border-green-300 hover:bg-green-100"
                      >
                        {isUpdating ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span>保存中...</span>
                          </>
                        ) : (
                          <>
                            <Save className="w-3 h-3" />
                            <span>保存</span>
                          </>
                        )}
                      </Button>
                      <Button 
                        onClick={cancelEditing} 
                        variant="ghost" 
                        size="sm" 
                        className="text-slate-600"
                      >
                        取消
                      </Button>
                    </>
                  ) : (
                    <Button 
                      onClick={startEditing} 
                      variant="ghost" 
                      size="sm" 
                      className="flex items-center gap-1 text-blue-600 hover:bg-blue-50"
                    >
                      <Edit className="w-3 h-3" />
                      <span>编辑</span>
                    </Button>
                  )}
                </div>
              )}
            </div>
            
            {isEditing ? (
              <div className="mt-3">
                <Textarea 
                  value={editableText} 
                  onChange={(e) => setEditableText(e.target.value)} 
                  className="min-h-[200px] text-sm border-green-200 resize-none focus:border-green-300 focus:ring-green-200"
                />
              </div>
            ) : (
              <div className="mt-3 text-green-700 whitespace-pre-wrap text-sm">
                {generatedText}
              </div>
            )}
          </div>
        )}
       

        {/* Generation Status */}
        {isGenerating && (
          <div className="w-full max-w-3xl mx-auto bg-gradient-to-r from-blue-100 to-cyan-100 rounded-2xl p-6 border border-blue-200">
            <div className="text-center space-y-3">
              <div className="flex items-center justify-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                <span className="text-blue-800 font-medium">AI 正在生成你的播客...</span>
              </div>
              <div className="w-full bg-white/50 rounded-full h-2">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full w-1/3 animate-pulse"></div>
              </div>
              <p className="text-blue-700 text-sm">
                正在调用后端API接口，请稍候...
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 播客列表区域 */}
      {/* 播客列表区域 */}
      <div className="w-full max-w-4xl mx-auto mt-12">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-bold text-slate-800">已创建播客</h2>
          <Button size="sm" variant="outline" onClick={fetchPodcastList} disabled={isLoadingList}>
            {isLoadingList ? <Loader2 className="w-4 h-4 animate-spin" /> : '刷新'}
          </Button>
        </div>
        {listError && (
          <div className="text-red-600 text-sm mb-2">{listError}</div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {podcastList.length === 0 && !isLoadingList && (
            <div className="text-slate-500 text-sm col-span-2">暂无播客内容</div>
          )}
          {podcastList.map((item, idx) => {
            const title = item.title || (item.content ? item.content.slice(0, 20) + (item.content.length > 20 ? '...' : '') : `播客#${item.id}`)
            const createdAt = item.created_at || item.createdAt
            return (
              <div
                key={item.id || idx}
                className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition cursor-pointer"
                onClick={() => { setSelectedPodcast(item); setDetailDialogOpen(true); }}
              >
                <div className="font-medium text-blue-700 truncate max-w-xs">{title}</div>
                <div className="text-xs text-slate-400 mt-2">{createdAt ? new Date(createdAt).toLocaleString() : ''}</div>
              </div>
            )
          })}
        </div>
      </div>
      {/* 详情弹窗 */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>播客详情</DialogTitle>
          </DialogHeader>
          {selectedPodcast && (
            <div className="space-y-2">
              <div><span className="font-semibold">ID：</span>{selectedPodcast.id}</div>
              <div>
                <span className="font-semibold">内容：</span>
                <div className="max-h-40 overflow-y-auto bg-slate-50 rounded p-2 mt-1 text-sm whitespace-pre-wrap border border-slate-100">
                  {selectedPodcast.content || '无内容'}
                </div>
              </div>
              <div><span className="font-semibold">音色ID：</span>{selectedPodcast.voice_ids || '无'}</div>
              <div><span className="font-semibold">内容类型：</span>{selectedPodcast.content_type || '无'}</div>
              <div>
                <span className="font-semibold">转写：</span>
                <div className="max-h-40 overflow-y-auto bg-slate-50 rounded p-2 mt-1 text-sm whitespace-pre-wrap border border-slate-100">
                  {selectedPodcast.transcript || '无转写'}
                </div>
              </div>
              <div><span className="font-semibold">创建时间：</span>{selectedPodcast.created_at ? new Date(selectedPodcast.created_at).toLocaleString() : ''}</div>
            </div>
          )}
        </DialogContent>
      </Dialog>      
    </div>
  )
}
