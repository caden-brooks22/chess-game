openings = {
    # Initial position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -" :
        ((1.0, "e2e4"),),

    # Response to e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -" :
        ((.75, "e7e5"), (.25, "e7e6")),

    # Response to e5
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -" :
        ((1.0, "g1f3"),),

    # Response to knight f3
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -" :
        ((.6, "b8c6"), (.4, "g8f6")),

    # Italian Game
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -" :
            ((.6, "f1c4"), (.4, "d2d3")),

        # Response to Italian Game
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -" :
        ((.7, "g8f6"), (.3, "b8c6")),

        # Fried Liver variation
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -" :
                ((.8, "f8c5"), (.2, "e8g8")),

            # Response to Fried Liver Attack
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -" :
                ((.9, "d2d4"), (.1, "c2c3")),

            "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq -" :
                ((.7, "e5d4"), (.3, "c6d4")),

            "r1bqkbnr/pppp1ppp/8/8/3nP3/5N2/PPP2PPP/RNBQKB1R w KQkq -" :
                ((.8, "g1d4"), (.2, "f1c4")),

            "r1bqkbnr/pppp1ppp/8/8/3NP3/8/PPP2PPP/RNBQKB1R b KQkq -" :
                ((.6, "d7d6"), (.4, "c7c6")),

    # Sicilian Defense
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -" :
        ((.8, "c7c5"), (.2, "e7e5")),

        # Response to Sicilian Defense
        "rnbqkbnr/pppp1ppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -" :
            ((.9, "g1f3"), (.1, "d2d4")),

        "rnbqkbnr/pppp1ppp/8/2p5/3PP3/8/PPP2PPP/RNBQKBNR b KQkq -" :
            ((.7, "b8c6"), (.3, "d7d6")),

        "r1bqkbnr/pppp1ppp/2n5/2p5/3PP3/8/PPP2PPP/RNBQKBNR w KQkq -" :
            ((.8, "g1f3"), (.2, "f1c4")),

    # French Defense
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -" :
            ((.7, "e7e6"), (.3, "d7d5")),

        # Response to French Defense
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -" :
            ((.8, "d2d4"), (.2, "b1c3")),

        "rnbqkbnr/pppppppp/8/3p4/3PP3/8/PPP2PPP/RNBQKBNR b KQkq -" :
            ((.6, "g8f6"), (.4, "c7c5")),

    # Caro-Kann Defense
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -" :
            ((.8, "c7c6"), (.2, "d7d5")),

        # Response to Caro-Kann Defense
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -" :
            ((.9, "d2d4"), (.1, "b1c3")),

        "rnbqkbnr/pppppppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR b KQkq -" :
            ((.7, "g8f6"), (.3, "c7c5")),
}