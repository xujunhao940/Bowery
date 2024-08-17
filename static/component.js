import {LitElement, html, css, unsafeCSS} from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

function gid() {
    function S4() {
        return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
    }

    return (S4() + S4() + S4() + S4() + S4() + S4() + S4() + S4());
}

class QuestionMessage extends LitElement {

    static properties = {
        text: {type: String}, image: {type: String}, _state: {state: true}
    }

    static styles = css`
        div {
            max-height: 100%;
            overflow-y: scroll;
            margin: 8px;
            padding: 16px;
            border-radius: 30px;
            background: rgba(var(--mdui-color-tertiary-container), .5);
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        p {
            margin: 0;
            line-height: 28px;
        }
    `

    constructor() {
        super()
        this.text = ""
        this.image = ""
        this._state = "pending"
    }

    render() {
        var imageTem
        if (this.image !== "Undefined") {
            imageTem = html`
                <b64-image className="b64-image" base64="${this.image}"></b64-image>`
        } else {
            imageTem = html``
        }

        return html`
            <div>
                <p>${this.text}</p>
                ${imageTem}
            </div>`
    }
}

window.customElements.define("question-message", QuestionMessage)


class AnswerMessage extends LitElement {

    static properties = {
        text: {type: String}, image: {type: String}, _state: {state: true}
    }

    static styles = css`
        div {
            max-height: 100%;
            overflow-y: scroll;
            margin: 8px;
            padding: 12px;
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        p {
            width: 100%;
            margin: 0;
            line-height: 28px;
        }

        mdui-button-icon {
            margin-left: auto;
        }
    `

    constructor() {
        super()
        this.text = ""
        this.image = ""
        this._state = "pending"
    }

    render() {
        var imageTem
        if (this.image !== "Undefined") {
            imageTem = html`
                <b64-image className="b64-image" base64="${this.image}"></b64-image>`
        } else {
            imageTem = html``
        }
        return html`
            <div>
                <mdui-button-icon icon="volume_up" onclick="speakNow('${this.text}')"></mdui-button-icon>
                <p>${this.text}</p>
                ${imageTem}
            </div>`
    }
}

window.customElements.define("answer-message", AnswerMessage)


class Image extends LitElement {
    static _id = gid()

    static properties = {
        base64: {type: String}, _expanded: {state: true}
    }

    static styles = css`
        .image-container {
            position: relative;
            width: 100%;
            height: 5rem;
            display: flex;
            justify-content: center;
            border-radius: 22px;
            overflow: hidden;
        }

        .image-button::slotted(*) {
            position: absolute;
            right: 4px;
            top: 4px;
        }

        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .image-container.expanded {
            height: unset;
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            padding: 12px;
            background: rgba(var(--mdui-color-primary-container), .5);
            z-index: 1;
            border-radius: 0;
        }

        .image-container.expanded img {
            object-fit: contain;
        }
    `

    constructor() {
        super()
        this.base64 = ""
        this._expanded = false
        this._id = gid()
    }

    _toggleExpanded() {
        this._expanded = !this._expanded
    }

    render() {
        if (this.base64 !== "Undefined") {
            return html`
                <div class="image-container ${this._expanded ? "expanded" : ""}">
                    <slot class="image-button" name="button"></slot>
                    <img src="data:image/png;base64,${this.base64}" @click="${this._toggleExpanded}"/>
                </div>`
        } else {
            return html``
        }
    }
}

window.customElements.define("b64-image", Image)
