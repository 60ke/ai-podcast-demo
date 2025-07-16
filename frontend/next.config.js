/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    distDir: 'out',
    // 支持URL前缀配置，可通过环境变量设置，默认为空
    basePath: process.env.BASE_PATH || '',
    // 设置资产前缀，跟随basePath或自定义CDN路径
    assetPrefix: process.env.ASSET_PREFIX || process.env.BASE_PATH || '',
    allowedDevOrigins: ["*.preview.same-app.com"],
    images: {
      unoptimized: true,
      domains: [
        "source.unsplash.com",
        "images.unsplash.com",
        "ext.same-assets.com",
        "ugc.same-assets.com",
      ],
      remotePatterns: [
        {
          protocol: "https",
          hostname: "source.unsplash.com",
          pathname: "/**",
        },
        {
          protocol: "https",
          hostname: "images.unsplash.com",
          pathname: "/**",
        },
        {
          protocol: "https",
          hostname: "ext.same-assets.com",
          pathname: "/**",
        },
        {
          protocol: "https",
          hostname: "ugc.same-assets.com",
          pathname: "/**",
        },
      ],
    },
    // 公开运行时配置给客户端
    publicRuntimeConfig: {
      basePath: process.env.BASE_PATH || 'http://localhost:8000',
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    },
  };
  
  module.exports = nextConfig;
  