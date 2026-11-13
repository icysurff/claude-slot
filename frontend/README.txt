Frontend (Stake Engine Web SDK) - Wild-Respin 5x4 "Racers Unlimited"

web-sdk-app/  -> in web-sdk/apps/wildrespin/ kopieren, dann im web-sdk-Ordner:
                 pnpm install
                 pnpm exec turbo run build --filter=wildrespin
                 pnpm run storybook --filter=wildrespin   (Port 6001)
Grafiken: web-sdk-app/static/assets/sprites/wr/  (H1-H5, L1-L8, W, S, W_expanded, frame, chest_*)
Preise der Kaeufe: src/game/betModeMeta.ts und src/game/config.ts - muessen zur Math passen.
