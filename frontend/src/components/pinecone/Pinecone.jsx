import { Database, LucideLoader2, MoveUp, RefreshCcw } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Textarea } from "../ui/textarea";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { useState } from "react";
import { Progress } from "../ui/progress";
import { updateDatabaseApi } from "@/api";

const Pinecone = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [indexname, setIndexName] = useState("");
    const [namespace, setNamespace] = useState("");

    const onStartUpload = async () => {
        const response = await updateDatabaseApi.updateDatabase(indexname, namespace);
        console.log(response);
        // await processStreamedProcess(response);
    }

    return (
        <main className="flex flex-col items-center p-24">
            <Card>
                <CardHeader>
                    <CardTitle>
                        Update Knowledge Base
                    </CardTitle>
                    <CardDescription>
                        Add new documents to your vector database
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                        <div className="col-span-2 grid gap-4 border rounded-lg p-6">
                            <div className="gap-4 relative">
                                <Button className="absolute -right-4 -top-4" variant={"ghost"} size={"icon"}>
                                    <RefreshCcw />
                                </Button>
                                <Label>Files List:</Label>
                                <Textarea readOnly className="min-h-24 resize-none border p-3 shadow-none disabled:cursor-default focus-visible:ring-0 text-sm text-muted-foreground"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label>Index Name</Label>
                                    <Input value={indexname} onChange={e => setIndexName(e.target.value)} placeholder="index name" disabled={isUploading} className="disabled:cursor-default" />
                                </div>
                                <div className="grid gap-2">
                                    <Label>Namespace</Label>
                                    <Input value={namespace} onChange={e => setNamespace(e.target.value)} placeholder="namespace" disabled={isUploading} className="disabled:cursor-default" />
                                </div>
                            </div>
                        </div>
                        <Button onClick={onStartUpload} variant={"outline"} className="w-full h-full" disabled={isUploading} >
                            <span className="flex flex-row">
                                <Database size={50} className="stroke-[#D90013]" />
                                <MoveUp className="stroke-[#D90013]" />
                            </span>
                        </Button>
                    </div>
                    {isUploading && <div className="mt-4">
                        <Label>File Name:</Label>
                        <div className="flex flex-row items-center gap-4">
                            <Progress value={80} />
                            <LucideLoader2 className="stroke-[#D90013] animate-spin" />
                        </div>
                    </div>}
                </CardContent>
            </Card>
        </main>
    )
};

export default Pinecone;
