-- Supabase 初始化 SQL 脚本
-- 在 Supabase SQL Editor 中执行此脚本

-- 1. 创建存储桶（如果不存在）
INSERT INTO storage.buckets (id, name, public)
VALUES ('markdown-files', 'markdown-files', true)
ON CONFLICT (id) DO NOTHING;

-- 2. 设置存储桶访问策略
-- 2.1 允许公开读取
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'markdown-files' );

-- 2.2 允许任何人上传文件
CREATE POLICY "Allow Upload"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'markdown-files' );

-- 2.3 允许更新文件
CREATE POLICY "Allow Update"
ON storage.objects FOR UPDATE
USING ( bucket_id = 'markdown-files' );

-- 3. 创建转换记录表
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    md_file_url TEXT,
    md_filename TEXT,
    download_media BOOLEAN DEFAULT false,
    media_count INTEGER DEFAULT 0,
    unique_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 设置 conversions 表的 RLS 策略
ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;

-- 允许任何人插入记录
CREATE POLICY "Allow Insert"
ON conversions FOR INSERT
WITH CHECK (true);

-- 允许任何人查询记录
CREATE POLICY "Allow Select"
ON conversions FOR SELECT
USING (true);

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS idx_conversions_url ON conversions(url);
CREATE INDEX IF NOT EXISTS idx_conversions_created_at ON conversions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversions_unique_id ON conversions(unique_id);

-- 6. 添加注释
COMMENT ON TABLE conversions IS '记录所有 URL 转换历史';
COMMENT ON COLUMN conversions.url IS '原始 URL';
COMMENT ON COLUMN conversions.md_file_url IS 'Markdown 文件公开访问 URL';
COMMENT ON COLUMN conversions.md_filename IS 'Markdown 文件名';
COMMENT ON COLUMN conversions.download_media IS '是否下载了媒体资源';
COMMENT ON COLUMN conversions.media_count IS '媒体文件数量';
COMMENT ON COLUMN conversions.unique_id IS '转换的唯一标识';

-- 7. 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversions_updated_at
    BEFORE UPDATE ON conversions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 8. 创建一个视图用于统计
CREATE OR REPLACE VIEW conversion_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_conversions,
    SUM(media_count) as total_media_files,
    COUNT(DISTINCT url) as unique_urls
FROM conversions
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMENT ON VIEW conversion_stats IS '按日期统计转换数据';

-- 9. 可选: 创建飞书集成相关的表
CREATE TABLE IF NOT EXISTS feishu_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id TEXT UNIQUE NOT NULL,
    app_token TEXT NOT NULL,
    table_id TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT DEFAULT '待处理',
    md_url TEXT,
    error_message TEXT,
    conversion_id UUID REFERENCES conversions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. 设置 feishu_records 表的 RLS 策略
ALTER TABLE feishu_records ENABLE ROW LEVEL SECURITY;

-- 允许任何人插入记录
CREATE POLICY "Allow Insert Feishu"
ON feishu_records FOR INSERT
WITH CHECK (true);

-- 允许任何人查询记录
CREATE POLICY "Allow Select Feishu"
ON feishu_records FOR SELECT
USING (true);

-- 允许更新记录
CREATE POLICY "Allow Update Feishu"
ON feishu_records FOR UPDATE
USING (true);

-- 11. 创建索引
CREATE INDEX IF NOT EXISTS idx_feishu_records_status ON feishu_records(status);
CREATE INDEX IF NOT EXISTS idx_feishu_records_created_at ON feishu_records(created_at DESC);

COMMENT ON TABLE feishu_records IS '飞书多维表格记录映射';

-- 完成
SELECT 'Supabase 初始化完成！' as message;
