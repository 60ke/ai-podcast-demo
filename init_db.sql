-- 数据库初始化脚本（MySQL 5.7）
-- 建议先创建数据库：CREATE DATABASE IF NOT EXISTS homework_bg DEFAULT CHARSET=utf8mb4;
-- 使用数据库：USE homework_bg;

-- 播客任务表
CREATE TABLE IF NOT EXISTS podcast_task (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID',
    content TEXT NOT NULL COMMENT '播客内容',
    voice_ids VARCHAR(255) NOT NULL COMMENT '播客音色素材ID列表，逗号分隔',
    tags VARCHAR(255) NOT NULL COMMENT '播客标签',
    status VARCHAR(32) DEFAULT 'pending' COMMENT '任务状态',
    user_id INT NOT NULL COMMENT '用户ID',
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 播客主表
CREATE TABLE IF NOT EXISTS podcast (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '播客ID',
    user_id INT NOT NULL COMMENT '用户ID',
    content TEXT NOT NULL COMMENT '播客内容摘要',
    voice_ids VARCHAR(255) NOT NULL COMMENT '播客音色素材ID列表，逗号分隔',
    tags VARCHAR(255) NOT NULL COMMENT '播客标签',
    mp3_url VARCHAR(512) NOT NULL COMMENT '播客音频URL',
    transcript TEXT COMMENT '播客完整脚本',
    ai_tags VARCHAR(255) COMMENT 'AI标签/内容类型',
    duration INT COMMENT '时长（秒）',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 评论表
CREATE TABLE IF NOT EXISTS podcast_comment (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID',
    podcast_id INT NOT NULL COMMENT '播客ID',
    user_id INT NOT NULL COMMENT '用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    INDEX idx_podcast_id (podcast_id),
    CONSTRAINT fk_comment_podcast FOREIGN KEY (podcast_id) REFERENCES podcast(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 点赞表
CREATE TABLE IF NOT EXISTS podcast_like (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞ID',
    podcast_id INT NOT NULL COMMENT '播客ID',
    user_id INT NOT NULL COMMENT '用户ID',
    INDEX idx_podcast_id (podcast_id),
    INDEX idx_user_id (user_id),
    CONSTRAINT fk_like_podcast FOREIGN KEY (podcast_id) REFERENCES podcast(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 