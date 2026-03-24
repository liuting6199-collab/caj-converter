#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAJ Converter Web - 后端API服务
提供CAJ文件上传、转换和下载功能
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp"
LIB_DIR = BASE_DIR / "lib"
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.caj', '.kdh', '.nh'}

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

import sys
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

conversion_tasks = {}


class ConversionTask(BaseModel):
    id: str
    filename: str
    status: str
    progress: int
    message: str
    output_file: Optional[str] = None
    created_at: str


class TaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    filename: str


def generate_task_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S_") + os.urandom(4).hex()


def validate_file_extension(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


async def convert_caj_to_pdf(input_path: Path, output_path: Path, task_id: str) -> bool:
    try:
        conversion_tasks[task_id]["status"] = "converting"
        conversion_tasks[task_id]["progress"] = 10
        conversion_tasks[task_id]["message"] = "正在准备转换..."

        print(f"🔄 开始转换任务 {task_id}")
        print(f"   输入文件: {input_path}")
        print(f"   输出文件: {output_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        conversion_tasks[task_id]["progress"] = 30
        conversion_tasks[task_id]["message"] = "正在解析CAJ文件..."

        try:
            import sys
            from pathlib import Path

            current_dir = Path(__file__).parent
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))

            from cajparser import CAJParser

            conversion_tasks[task_id]["progress"] = 50
            conversion_tasks[task_id]["message"] = "正在转换..."

            caj = CAJParser(str(input_path))
            caj.convert(str(output_path))

            conversion_tasks[task_id]["progress"] = 80
            conversion_tasks[task_id]["message"] = "正在保存PDF..."

            if output_path.exists() and output_path.stat().st_size > 0:
                conversion_tasks[task_id]["progress"] = 100
                conversion_tasks[task_id]["status"] = "completed"
                conversion_tasks[task_id]["message"] = "转换成功"
                conversion_tasks[task_id]["output_file"] = str(output_path)
                print(f"✅ 转换成功: {task_id}")
                print(f"   输出文件大小: {output_path.stat().st_size} bytes")
                return True
            else:
                conversion_tasks[task_id]["status"] = "failed"
                conversion_tasks[task_id]["message"] = "转换失败：未生成PDF文件"
                print(f"❌ 转换失败: {task_id} - 未生成PDF文件")
                return False

        except Exception as e:
            error_msg = str(e)
            print(f"❌ caj2pdf转换异常: {error_msg}")
            import traceback
            traceback.print_exc()

            conversion_tasks[task_id]["status"] = "failed"
            conversion_tasks[task_id]["message"] = f"转换失败: {error_msg[:100]}"
            return False

    except Exception as e:
        error_msg = str(e)
        conversion_tasks[task_id]["status"] = "failed"
        conversion_tasks[task_id]["message"] = f"转换异常: {error_msg[:100]}"
        print(f"❌ 转换异常: {task_id} - {error_msg}")
        import traceback
        traceback.print_exc()
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 CAJ Converter 服务启动中...")

    current_time = datetime.now().timestamp()
    for dir_path in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
        if dir_path.exists():
            for file_path in dir_path.iterdir():
                try:
                    if file_path.is_file():
                        file_time = file_path.stat().st_mtime
                        if current_time - file_time > 86400:
                            file_path.unlink()
                            print(f"🗑️ 清理旧文件: {file_path}")
                except Exception as e:
                    print(f"⚠️ 清理文件失败: {file_path}, 错误: {e}")

    yield

    print("🛑 CAJ Converter 服务关闭")


app = FastAPI(
    title="CAJ Converter Web",
    description="CAJ文件批量转PDF工具",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload", response_model=TaskResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        print(f"📥 收到上传请求: {file.filename}")

        if not file.filename:
            print("❌ 文件名为空")
            raise HTTPException(status_code=400, detail="文件名不能为空")

        print(f"🔍 验证文件扩展名: {file.filename}")
        if not validate_file_extension(file.filename):
            allowed = ', '.join(ALLOWED_EXTENSIONS)
            print(f"❌ 不支持的文件格式: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。只允许: {allowed}"
            )

        task_id = generate_task_id()
        print(f"🆔 生成任务ID: {task_id}")

        upload_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
        output_path = OUTPUT_DIR / f"{task_id}_{Path(file.filename).stem}.pdf"
        print(f"💾 保存路径: {upload_path}")

        content = await file.read()
        print(f"📊 文件大小: {len(content)} bytes")

        if len(content) > MAX_FILE_SIZE:
            print(f"❌ 文件过大: {len(content)} bytes")
            raise HTTPException(status_code=400, detail="文件大小超过50MB限制")

        async with aiofiles.open(upload_path, 'wb') as f:
            await f.write(content)
        print(f"✅ 文件保存成功")

        conversion_tasks[task_id] = {
            "id": task_id,
            "filename": file.filename,
            "status": "pending",
            "progress": 0,
            "message": "等待转换",
            "output_file": None,
            "upload_path": str(upload_path),
            "output_path": str(output_path),
            "created_at": datetime.now().isoformat()
        }

        background_tasks.add_task(
            convert_caj_to_pdf,
            upload_path,
            output_path,
            task_id
        )

        print(f"✅ 任务创建成功: {task_id}")

        return TaskResponse(
            success=True,
            message="文件上传成功，开始转换",
            task_id=task_id
        )

    except HTTPException as he:
        print(f"❌ HTTP异常: {he.detail}")
        raise
    except Exception as e:
        print(f"❌ 上传异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.post("/api/upload/batch", response_model=List[TaskResponse])
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    responses = []

    for file in files:
        try:
            if not file.filename or not validate_file_extension(file.filename):
                responses.append(TaskResponse(
                    success=False,
                    message=f"文件 {file.filename} 格式不支持",
                    task_id=None
                ))
                continue

            task_id = generate_task_id()
            upload_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
            output_path = OUTPUT_DIR / f"{task_id}_{Path(file.filename).stem}.pdf"

            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                responses.append(TaskResponse(
                    success=False,
                    message=f"文件 {file.filename} 超过大小限制",
                    task_id=None
                ))
                continue

            async with aiofiles.open(upload_path, 'wb') as f:
                await f.write(content)

            conversion_tasks[task_id] = {
                "id": task_id,
                "filename": file.filename,
                "status": "pending",
                "progress": 0,
                "message": "等待转换",
                "output_file": None,
                "upload_path": str(upload_path),
                "output_path": str(output_path),
                "created_at": datetime.now().isoformat()
            }

            background_tasks.add_task(
                convert_caj_to_pdf,
                upload_path,
                output_path,
                task_id
            )

            responses.append(TaskResponse(
                success=True,
                message="上传成功",
                task_id=task_id
            ))

        except Exception as e:
            responses.append(TaskResponse(
                success=False,
                message=f"上传失败: {str(e)}",
                task_id=None
            ))

    return responses


@app.get("/api/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    if task_id not in conversion_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = conversion_tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        filename=task["filename"]
    )


@app.get("/api/tasks")
async def get_all_tasks():
    return list(conversion_tasks.values())


@app.get("/api/download/batch")
async def download_batch(request: Request):
    task_ids = request.query_params.get("task_ids", "")
    print(f"📦 收到批量下载请求: {task_ids}")

    ids = task_ids.split(',')
    ids = [id.strip() for id in ids if id.strip()]

    if not ids:
        print("❌ 未指定任务ID")
        raise HTTPException(status_code=400, detail="未指定任务ID")

    print(f"📋 任务ID列表: {ids}")

    zip_filename = f"batch_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = TEMP_DIR / zip_filename

    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for task_id in ids:
            print(f"   处理任务: {task_id}")
            if task_id in conversion_tasks:
                task = conversion_tasks[task_id]
                print(f"      状态: {task['status']}")
                print(f"      output_file: {task.get('output_file')}")
                print(f"      output_path: {task.get('output_path')}")

                if task["status"] == "completed":
                    output_path_str = task.get("output_file") or task.get("output_path")
                    if output_path_str:
                        output_file = Path(output_path_str)
                        print(f"      文件路径: {output_file}")
                        print(f"      文件存在: {output_file.exists()}")
                        if output_file.exists():
                            arcname = f"{Path(task['filename']).stem}.pdf"
                            zipf.write(output_file, arcname)
                            file_count += 1
                            print(f"      ✅ 已添加: {arcname}")
                        else:
                            print(f"      ❌ 文件不存在: {output_file}")
                    else:
                        print(f"      ❌ 没有输出路径")
                else:
                    print(f"      ⏭️ 任务未完成，跳过")

    print(f"📦 ZIP文件创建完成，包含 {file_count} 个文件")

    if not zip_path.exists() or zip_path.stat().st_size == 0:
        print("❌ 没有可下载的文件")
        raise HTTPException(status_code=400, detail="没有可下载的文件")

    print(f"✅ 返回ZIP文件: {zip_path}, 大小: {zip_path.stat().st_size} bytes")

    return FileResponse(
        path=zip_path,
        filename=zip_filename,
        media_type="application/zip"
    )


@app.get("/api/download/{task_id}")
async def download_file(task_id: str):
    if task_id not in conversion_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = conversion_tasks[task_id]

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="文件尚未转换完成")

    output_file = Path(task["output_path"])
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="输出文件不存在")

    return FileResponse(
        path=output_file,
        filename=f"{Path(task['filename']).stem}.pdf",
        media_type="application/pdf"
    )


@app.delete("/api/task/{task_id}")
async def delete_task(task_id: str):
    if task_id not in conversion_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = conversion_tasks[task_id]

    try:
        upload_path = Path(task["upload_path"])
        if upload_path.exists():
            upload_path.unlink()
    except:
        pass

    try:
        output_path = Path(task["output_path"])
        if output_path.exists():
            output_path.unlink()
    except:
        pass

    del conversion_tasks[task_id]

    return {"success": True, "message": "任务已删除"}


@app.delete("/api/tasks")
async def clear_all_tasks():
    for task_id, task in list(conversion_tasks.items()):
        try:
            upload_path = Path(task["upload_path"])
            if upload_path.exists():
                upload_path.unlink()
        except:
            pass

        try:
            output_path = Path(task["output_path"])
            if output_path.exists():
                output_path.unlink()
        except:
            pass

    conversion_tasks.clear()

    return {"success": True, "message": "所有任务已清空"}


app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend" / "static"), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)