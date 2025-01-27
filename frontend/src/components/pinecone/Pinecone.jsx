import { Database } from "lucide-react";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";


const Pinecone = () => {
  return (
        <div className="flex flex-col items-center p-24">
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

                        </div>
                        <Button variant="outline" className="w-full h-full">
                            <Database size={50} />
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
  )
};

export default Pinecone;
    