"use client";

import { CitationModel } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, FileText } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { motion } from "framer-motion";

interface Props {
  citations?: CitationModel[];
}

export const Citations = ({ citations }: Props) => {
  const [selectedCitation, setSelectedCitation] = useState<CitationModel | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <>
      <div className="mt-6 pt-6 border-t border-white/5">
        <div className="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4" /> Cited Sources
        </div>
        <ScrollArea className="h-48">
          <div className="space-y-3 pr-4">
            {citations.map((cite, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <Card 
                  className="bg-secondary/10 border-white/5 cursor-pointer hover:border-primary/50 transition-colors"
                  onClick={() => setSelectedCitation(cite)}
                >
                  <CardContent className="p-3">
                    <div className="flex items-start justify-between mb-2">
                      <div className="text-xs font-semibold text-primary truncate mr-2 flex items-center gap-1">
                        <FileText className="w-3 h-3" /> {cite.sourceFile}
                      </div>
                      <Badge variant="outline" className="text-[10px] h-5 py-0 px-1 bg-black/20 shrink-0">
                        {cite.category}
                      </Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-2 leading-relaxed italic">
                      Click to preview content...
                    </p>
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5 text-[10px] text-muted-foreground">
                      <span>Match: {(cite.score * 100).toFixed(1)}%</span>
                      <span className="uppercase text-primary/50">{cite.scoreType}</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </ScrollArea>
      </div>

      <Sheet open={!!selectedCitation} onOpenChange={(o) => !o && setSelectedCitation(null)}>
        <SheetContent className="bg-background/95 backdrop-blur-xl border-white/10 sm:max-w-md">
          <SheetHeader className="mb-6">
            <SheetTitle className="flex items-center gap-2 text-primary">
              <FileText className="w-5 h-5" /> 
              {selectedCitation?.sourceFile}
            </SheetTitle>
            <SheetDescription className="flex items-center gap-4">
              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
                {selectedCitation?.category}
              </Badge>
              <span className="text-xs">
                {selectedCitation?.scoreType}: {(selectedCitation?.score ?? 0 * 100).toFixed(1)}%
              </span>
            </SheetDescription>
          </SheetHeader>
          
          <div className="p-4 rounded-xl bg-secondary/20 border border-white/5 text-sm leading-relaxed text-foreground overflow-y-auto max-h-[70vh]">
            {selectedCitation?.chunkPreview}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
};
