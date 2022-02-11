"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MultiCoreBinding = exports.Binding = void 0;
const events_1 = require("events");
const process = require("process");
class Binding extends events_1.EventEmitter {
    constructor() {
        super();
        this.connected = false;
        this.overload_quiet = false;
        this.multi_thread = false;
        this.promises = new Map();
        this.listPendingUpdates = new Map();
        this.activeUpdates = new Map();
        process.stdin.on('data', (chunk) => {
            try {
                const list_data = chunk.toString().split('}{').join('}\n{').split('\n');
                for (let i = 0; i < list_data.length; i++) {
                    const data = JSON.parse(list_data[i]);
                    if (data.try_connect == 'connected') {
                        this.connected = true;
                        this.overload_quiet = data.overload_quiet;
                        this.multi_thread = data.multi_thread;
                        Binding.sendInternalUpdate({
                            ping: true,
                        });
                        setInterval(() => Binding.sendInternalUpdate({
                            ping: true,
                        }), 10000);
                        setInterval(() => {
                            this.listPendingUpdates.forEach((value, chat_id) => {
                                value.forEach((update_saved, update_id) => {
                                    if (!this.activeUpdates.get(chat_id)) {
                                        this.activeUpdates.set(chat_id, true);
                                        this.emit('request', update_saved, update_id);
                                    }
                                });
                            });
                        }, 50);
                        this.emit('connect', data.user_id);
                    }
                    else if (data.ping_with_response) {
                        Binding.sendInternalUpdate({
                            ping_with_response: true,
                            sid: data.sid,
                        });
                    }
                    else if (data.ssid == this.ssid) {
                        if (data.uid !== undefined) {
                            const promise = this.promises.get(data.uid);
                            if (promise) {
                                if (data.data !== undefined) {
                                    promise(data.data);
                                }
                                else {
                                    promise(null);
                                }
                            }
                        }
                        else {
                            this.appendUpdate(data.data);
                        }
                    }
                }
            }
            catch (e) {
                console.log(e);
                Binding.log('Invalid Binding Update', Binding.ERROR);
            }
        });
        this.ssid = Binding.makeID(12);
        Binding.sendInternalUpdate({
            try_connect: this.ssid,
        });
    }
    appendUpdate(update) {
        const chat_id = update.chat_id;
        let pending_updates = this.listPendingUpdates.get(chat_id);
        const updateID = Binding.makeID(12);
        if (!pending_updates) {
            pending_updates = new Map();
            pending_updates.set(updateID, update);
            this.listPendingUpdates.set(chat_id, pending_updates);
        }
        else {
            pending_updates.set(updateID, update);
        }
    }
    resolveUpdate(chat_id, update_id) {
        let pending_updates = this.listPendingUpdates.get(chat_id);
        pending_updates?.delete(update_id);
        if (pending_updates?.size == 0) {
            this.listPendingUpdates.delete(chat_id);
        }
        this.activeUpdates.delete(chat_id);
    }
    async sendUpdate(update) {
        if (this.connected) {
            const uid = Binding.makeID(12);
            Binding.sendInternalUpdate({
                uid,
                data: update,
                ssid: this.ssid,
            });
            return new Promise(resolve => {
                this.promises.set(uid, (data) => {
                    resolve(data);
                    this.promises.delete(uid);
                });
            });
        }
        else {
            throw new Error('No connected client');
        }
    }
    static log(message, verbose_mode) {
        Binding.sendInternalUpdate({
            log_message: message,
            verbose_mode: verbose_mode,
        });
    }
    static makeID(length) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }
    static sendInternalUpdate(update) {
        console.log(JSON.stringify(update));
    }
}
exports.Binding = Binding;
Binding.DEBUG = 1;
Binding.INFO = 2;
Binding.WARNING = 3;
Binding.ERROR = 4;
class MultiCoreBinding {
    constructor(process_multicore) {
        this.process_multicore = process_multicore;
        this.promises = new Map();
    }
    resolveUpdate(data) {
        const promise = this.promises.get(data.uid);
        if (promise) {
            if (data.result !== undefined) {
                promise(data.result);
            }
            else {
                promise(null);
            }
        }
    }
    async sendUpdate(update) {
        const uid = MultiCoreBinding.makeID(12);
        this.process_multicore.postMessage({
            action: 'binding_update',
            uid: uid,
            update: update,
        });
        return new Promise(resolve => {
            this.promises.set(uid, (data) => {
                resolve(data);
                this.promises.delete(uid);
            });
        });
    }
    static makeID(length) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }
}
exports.MultiCoreBinding = MultiCoreBinding;
