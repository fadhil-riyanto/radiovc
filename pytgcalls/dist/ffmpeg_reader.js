"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FFmpegReader = void 0;
const child_process_1 = require("child_process");
const binding_1 = require("./binding");
const buffer_optimized_1 = require("./buffer_optimized");
class FFmpegReader {
    constructor(additional_parameters) {
        this.total_size = 0;
        this.MAX_READ_BUFFER = 65536 * 4;
        this.MAX_SIZE_BUFFERED = 5 * this.MAX_READ_BUFFER;
        this.paused = true;
        this.stopped = false;
        this.additional_parameters = '';
        this.almostFinished = false;
        this.haveEnd = true;
        this.dataListener = (async (chunk) => {
            this.total_size += chunk.length;
            this.bytes_read.push(chunk);
            if (this.bytes_read.length >= this.MAX_SIZE_BUFFERED) {
                this.fifo_reader?.stdout.pause();
            }
        });
        this.endListener = (async () => {
            this.almostFinished = true;
        });
        this.bytes_read = new buffer_optimized_1.BufferOptimized(0);
        this.additional_parameters = additional_parameters.includes('-atend') ? additional_parameters : additional_parameters + '-atend';
    }
    convert_audio(path, bitrate) {
        let list_cmd = this.additional_parameters.split('-atend');
        this.start_conversion(list_cmd[0].split(':_cmd_:').concat([
            '-i',
            path.replace('fifo://', ''),
            '-f',
            's16le',
            '-ac',
            '1',
            '-ar',
            bitrate,
            'pipe:1',
        ]).concat(list_cmd[1].split(':_cmd_:')));
    }
    convert_video(path, width, height, framerate) {
        let list_cmd = this.additional_parameters.split('-atend');
        if (path.includes('image:')) {
            list_cmd[0] = list_cmd[0] + ':_cmd_:-loop:_cmd_:1:_cmd_:-framerate:_cmd_:1';
            this.haveEnd = false;
        }
        this.start_conversion(list_cmd[0].split(':_cmd_:').concat([
            '-i',
            path.replace('fifo://', '').replace('image:', ''),
            '-f',
            'rawvideo',
            '-pix_fmt',
            'yuv420p',
            '-r',
            framerate,
            '-vf',
            'scale=' + width + ':' + height,
            'pipe:1',
        ]).concat(list_cmd[1].split(':_cmd_:')));
    }
    start_conversion(params) {
        params = params.filter(e => e);
        binding_1.Binding.log('RUNNING_FFMPEG_COMMAND -> ffmpeg ' + params.join(' '), binding_1.Binding.INFO);
        this.fifo_reader = (0, child_process_1.spawn)('ffmpeg', params);
        this.fifo_reader.stdout.on('data', this.dataListener);
        this.fifo_reader.stderr.on('data', async (chunk) => {
            const message = chunk.toString();
            if (message.includes('] Opening')) {
                binding_1.Binding.log('OPENING_M3U8_SOURCE -> ' + (new Date().getTime()), binding_1.Binding.DEBUG);
            }
            else if (message.includes('] Unable')) {
                let list_err = message.split('\n');
                for (let i = 0; i < list_err.length; i++) {
                    if (list_err[i].includes('] Unable')) {
                        binding_1.Binding.log(list_err[i], binding_1.Binding.ERROR);
                        break;
                    }
                }
            }
        });
        this.fifo_reader.on('close', this.endListener);
        this.processBytes();
    }
    processBytes() {
        const oldTime = new Date().getTime();
        if (this.stopped) {
            return;
        }
        if (!this.paused) {
            if (this.bytes_read.length > 0) {
                if (this.bytes_read.length < this.MAX_SIZE_BUFFERED) {
                    this.fifo_reader?.stdout.resume();
                }
                this.bytes_read.byteLength = this.bytes_read.length < this.MAX_READ_BUFFER ? this.bytes_read.length : this.MAX_READ_BUFFER;
                if (this.onData != undefined) {
                    const buffer = this.bytes_read.readBytes();
                    this.onData(buffer);
                }
            }
            else if (this.almostFinished) {
                if (this.onEnd != undefined) {
                    this.onEnd();
                }
                this.fifo_reader?.kill();
                return;
            }
        }
        const toSubtract = new Date().getTime() - oldTime;
        setTimeout(async () => this.processBytes(), 5 - toSubtract);
    }
    pause() {
        this.paused = true;
    }
    resume() {
        this.paused = false;
    }
    fileSize() {
        return this.total_size;
    }
    stop() {
        this.fifo_reader?.stdout.removeListener('data', this.dataListener);
        this.fifo_reader?.removeListener('close', this.endListener);
        this.stopped = true;
        this.fifo_reader?.stdout.pause();
        this.fifo_reader?.kill('SIGKILL');
    }
}
exports.FFmpegReader = FFmpegReader;
