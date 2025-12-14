import logging
import os
from fastapi import APIRouter
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from yt_dlp.utils import DownloadError
from ..config import AppConfig, get_config
from ..constants.download import YOUTUBE_URL_PREFIX
from ..models.transcription import URLTranscriptionRequest, TranscriptionResponse
from ..services.download.youtube import download_from_youtube
from ..services.download.local import download_to_fs
from ..services.transcription import transcribe_audio


router = APIRouter(tags=["Transcription"])
config: AppConfig = get_config()


@router.post("/url")
async def get_transcription_from_url(payload: URLTranscriptionRequest):
    url = payload.url
    try:
        for yt_prefix in YOUTUBE_URL_PREFIX:
            if url.startswith(yt_prefix):
                logging.info(f"Downloading from YouTube: {url}")
                output_path, error = download_from_youtube(url)
                if error or not output_path:
                    return JSONResponse(
                        status_code=500,
                        content=TranscriptionResponse(
                            message=f"Failed to download YouTube video due to an internal error."
                        ).dict(),
                    )
                segment_data = transcribe_audio(output_path)
                return JSONResponse(
                    status_code=200,
                    content=TranscriptionResponse(
                        success=True,
                        message="Transcription from URL successful",
                        data=segment_data,
                    ).dict(),
                )

    except DownloadError as dle:
        return JSONResponse(
            status=500,
            content=TranscriptionResponse(
                message=f"Failed to download video due to the following error: {dle}"
            ).dict(),
        )

    except Exception as exc:
        return JSONResponse(
            status=500,
            content=TranscriptionResponse(
                message=f"Failed to transcribe video from URL due to the following error: {exc}"
            ).dict(),
        )


@router.post("/file")
async def get_transcription_from_file(file: UploadFile = File(...)):
    try:
        output_path, error = download_to_fs(url)
        if error or not output_path:
            return JSONResponse(
                status_code=500,
                content=TranscriptionResponse(
                    message=f"Failed to download YouTube video due to an internal error."
                ).dict(),
            )
        segment_data = transcribe_audio(output_path)
        return JSONResponse(
            status_code=200,
            content=TranscriptionResponse(
                success=True,
                message="Transcription from URL successful",
                data=segment_data,
            ).dict(),
        )

    except Exception as exc:
        return JSONResponse(
            status=500,
            content=TranscriptionResponse(
                message=f"Failed to transcribe video from URL due to the following error: {exc}"
            ).dict(),
        )
