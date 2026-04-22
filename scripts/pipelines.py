import scrapy
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter
from urllib.parse import unquote

class AlgicMediaPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter.get('file_urls', []):
            # unquote handles special chars like $ in S3 URLs for Myaamia
            yield scrapy.Request(unquote(file_url), meta={'iso': item.get('iso'), 'id': item.get('id')})

    def file_path(self, request, response=None, info=None, *, item=None):
        iso = request.meta.get('iso', 'unk')
        entry_id = request.meta.get('id', 'unlabeled')
        parts = request.url.split('.')
        ext = parts[-1].split('?')[0] if len(parts) > 1 else 'mp3'
        return f"{iso}/{entry_id}.{ext}"