from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.views import NBaselViewSet
from apps.core.models import Asset, Project
from apps.core.models.asset import ASSET_UPLOAD_SOURCE
from apps.core.serializers import AssetSerializer
from apps.core.models.asset import ASSET_FILE_TYPE

class AssetViewSet(NBaselViewSet):
    name = "asset"
    serializer_class = AssetSerializer

    def get_queryset(self):
        return Asset.objects.all()

    @action(detail=False, methods=["post"])
    def create_assets_for_project(self, request):
        files = request.FILES.getlist("files")
        project_id = request.data.get("project_id")

        if not files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        assets = []
        for file in files:
            asset = Asset(
                name=file.name,
                description=f"Uploaded file: {file.name}",
                project=project,
                upload_source=ASSET_UPLOAD_SOURCE.UPLOAD,
                file_type=self.get_file_type(file.name),
                owner=request.user,
            )
            asset.save()

            # Save the file using Django's default file storage
            file_path = default_storage.save(f"assets/{asset.id}/{file.name}", file)
            asset.url = default_storage.url(file_path)
            asset.save()

        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_file_type(self, filename):
        extension = filename.split(".")[-1].lower()
        if extension == "pdf":
            return ASSET_FILE_TYPE.PDF
        elif extension in ["doc", "docx"]:
            return ASSET_FILE_TYPE.DOC
        elif extension == "txt":
            return ASSET_FILE_TYPE.TXT
        else:
            return ASSET_FILE_TYPE.OTHER
