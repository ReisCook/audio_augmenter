from praatio import textgrid

class TextGridHandler:
    def read_textgrid(self, file_path):
        return textgrid.openTextgrid(file_path, includeEmptyIntervals=True)

    def write_textgrid(self, file_path, tg_data):
        tg_data.save(file_path, format="short_textgrid", includeBlankSpaces=True)

    def create_synthetic_textgrid(self, intervals, duration):
        tg = textgrid.Textgrid()
        tier = textgrid.IntervalTier('vocalizations', [])
        
        for start, end, label in intervals:
            tier.addInterval(textgrid.Interval(start, end, label))
        
        # Add a final interval to cover any remaining time
        if intervals:
            last_end = max(end for _, end, _ in intervals)
            if last_end < duration:
                tier.addInterval(textgrid.Interval(last_end, duration, ''))
        else:
            tier.addInterval(textgrid.Interval(0, duration, ''))
        
        tg.addTier(tier)
        return tg

    def extract_vocalization_segments(self, tg_data, labels):
        segments = []
        for interval in tg_data.tierDict['vocalizations'].entryList:
            if interval.label in labels:
                segments.append((interval.start, interval.end, interval.label))
        return segments