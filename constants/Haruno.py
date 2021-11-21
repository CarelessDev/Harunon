COLOR = 0x5a3844


class Words:
    JOIN = "お姉さんが入った!"
    LEAVE = "じゃ またねええ!"

    NOW_PLAYING = "Now Playing..."
    ENQUEUED = "Enqueued"

    class Skip:
        NOT_PLAYING = "Not playing any music right now..."
        SUCCESS = "スキップ成功!"

    class Pause:
        NOT_PLAYING = "Not playing any music right now..."
        SUCCESS = "Paused"

    class Resume:
        SUCCESS = "Resumed"

    class Queue:
        EMPTY = "Queue is currently empty."
        CLEARED = "Queue cleared! 成功!"

    class Loop:
        ON = "ループしま～す!"
        OFF = "ループしません"


class Emoji:
    SKIP = "⏭"
    PAUSE_RESUME = "⏯"

    class Loop:
        # * Recommended by GitHub Copilot ✨✨✨
        ON = "🔁"
        OFF = "🔂"
